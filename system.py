"""This is the main script file, use `python system.py` to run the software.

    Attributes:
        OUTPATH: path to save output images.
        INPATH: path to save the detected input images.
        BENCHMARCH_TIME: enable time cost tracking function.
"""
import copy

import torchvision
import sys, os
import threading
from database.FaceData import FaceData

from threads.SharedData import SharedData
from facialDetection.webcamFDM import webcamFDM
from facialDetection.directoryFDM import directoryFDM
from Utilities import *
import time
from superResolution.Srgan_Utils import *
from FaceRec.Rec_Utils import *

OUTPATH = './out'
INPATH = './input'
BENCHMARK_TIME = True

os.makedirs(OUTPATH, exist_ok=True)
os.makedirs(INPATH, exist_ok=True)
memory = SharedData()
controller = None

hardware = None
srganModel = None
recogModel = None


def set_controller(control_bbj):
    global controller
    controller = control_bbj

    init_models()

def init_models():
    global hardware, srganModel, recogModel

    hardware = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    srganModel = superResolutionModel(hardware)
    recogModel = recognitionModel("./images", hardware)

def start(inputMode):
    """Start function, linked with GUI to start threads.
    Called when detection starts.

    Args:
        interface (userInteface.UI_Main.UI_MainWindow): GUI object
        inputMode (int): choose which model to run detection. 0 for importing images, 1 for using camera.
    """
    memory.reset()
    threads = []
    detect = chooseDetectionMode(inputMode)
    threads.append(detect)
    gan = threading.Thread(target = ganManager, args = [srganModel])
    threads.append(gan)
    recog = threading.Thread(target = recogManager, args = [recogModel, controller])
    threads.append(recog)
    for thread in threads:
        thread.start()
    print("finished")

def chooseDetectionMode(inputMode):
    """Used to choose which detection model to use, called by start function.

    Args:
        interface (userInteface.UI_Main.UI_MainWindow): GUI object
        inputMode (int): choose which model to run detection. 0 for importing images, 1 for using camera.
    """
    if (inputMode == 0):
        return threading.Thread(target = detectionManagerDirectory, args = [controller])
    if (inputMode == 1):
        return threading.Thread(target = detectionManagerWebcam, args = [controller])


def detectionManagerDirectory(controller):
    """Use imported image/video to detect faces.

    Args:
        interface (userInteface.UI_Main.UI_MainWindow): GUI object
    """
    print("DET: start")
    FDM = directoryFDM(controller,memory)
    if BENCHMARK_TIME:
        start = time.time()
    FDM.run(testForGAN, cv2_to_tensor)
    if BENCHMARK_TIME:
        elapsed = (time.time() - start)
        print('FACE DETECTION: ' + str(elapsed) + 's')
    memory.detDone.set()
    memory.ganQueueCount.release()
    memory.recogQueueCount.release()
    print("DET: done")
    return

def empty_all_queues():
    """ For some reason legacy code used custom queue"""
    gan_queue = memory.ganQueue
    rec_queue = memory.recogQueue
    while gan_queue.head is not None:
        gan_queue.pop()

    while rec_queue.head is not None:
        rec_queue.pop()


def add_corrected_face(name, face):
    recogModel.add_face(name, face)


def detectionManagerWebcam(controller):
    """Use camera to record video and detect faces.

    Args:
        interface (userInteface.UI_Main.UI_MainWindow): GUI object
    """
    print("DET: start")
    FDM = webcamFDM(controller,memory)
    CAM = cv2.VideoCapture(0)

    try:
        if BENCHMARK_TIME:
            start = time.time()
        FDM.run(CAM, testForGAN, cv2_to_tensor)
        if BENCHMARK_TIME:
            elapsed = (time.time() - start)
            print('FACE DETECTION WEBCAM: ' + str(elapsed) + 'ns')
    except RuntimeError:
    # TODO: WRITE TO ERROR LOG
        raise

    memory.detDone.set()
    memory.ganQueueCount.release()
    memory.recogQueueCount.release()
    print("DET: done")
    return


def ganManager(srganModel):
    """ Super Resolution Section
        Checks if the image is too small (SRGAN has worse performance for  < 64bit images)
        If so apply double the size using Bicubic Interpolation
        Super Resolution is then applied
    
    Args:
        #TODO: redo
        interface (userInteface.UI_Main.UI_MainWindow): GUI object
    """
    generator = Generator(4).eval()
    print("\tGAN: start")
    i = 0
    while (1):
        memory.ganQueueCount.acquire()
        if memory.detDone.is_set() and memory.ganQueue.empty():
            print("\tGAN: done")
            memory.ganDone.set()
            memory.recogQueueCount.release()
            return

        face_data_to_process = memory.ganQueue.pop()

        print("\tGAN: doing")
        if face_data_to_process is None:
            print("\tGAN: error 0")
            return

        num_retries = 1
        for attempt_no in range(num_retries):
            try:
                if BENCHMARK_TIME:
                    start = time.time()
                image_data = face_data_to_process.get_data()
                torchvision.utils.save_image(image_data.clone(), "./out/" + "beforeSuperResolution" + str(i) + ".png")

                tensor = srganModel.super_resolution(image_data)
  
                if BENCHMARK_TIME:
                    elapsed = (time.time() - start)
                    print('\tSUPER RESOLUTION: ' + str(elapsed) + 's')
                break
            except RuntimeError as err:
                print("Error: OOM")
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            # TODO: WRITE TO ERROR LOG
                raise err

        # shift the image to the range (0, 1), by subtracting the minimum and dividing by the maximum pixel value range.
        min_v = torch.min(tensor)
        range_v = torch.max(tensor) - min_v
        if range_v > 0:
            normalised = (tensor - min_v) / range_v
        else:
            normalised = torch.zeros(tensor.size())

        torchvision.utils.save_image(normalised.clone(), "./out/" + "AfterSuperResolution" + str(i) + ".png")

        i += 1
        face_data_to_process.set_data(normalised)
        print("HERE GAN v2", face_data_to_process)
        memory.recogQueue.push(face_data_to_process)
        memory.recogQueueCount.release()


def recogManager(recogModel, controller):
    """Face recognition section, will process all pictures in recognition queue in order.

    Args:
        interface (userInteface.UI_Main.UI_MainWindow): GUI object
    """

    i = 0
    while (1):
        memory.recogQueueCount.acquire()
        if (memory.detDone.is_set() and memory.ganDone.is_set() and memory.recogQueue.empty()):
           #TODO: Button disabling
            return
            print("\t\tREC: done")

        face_data_to_process = memory.recogQueue.pop()

        print("\t\tREC: doing")
        if (face_data_to_process is None):
            print("\t\tREC: queue empty")
        else:
            try:
                if BENCHMARK_TIME:
                    start = time.time()
                    image_data = face_data_to_process.get_data()
                confidence, label = recogModel.recognize(image_data)
                if BENCHMARK_TIME:
                    elapsed = (time.time() - start)
                    print('\tFace Recognition: ' + str(elapsed) + 's')
                    print('\tName: ' + label + ", Confidence: " + str(confidence))
            except RuntimeError:
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            # TODO: WRITE TO ERROR LOG
                raise

            if(confidence <= 50):
                if confidence >= 20:
                    label = "Unknown ("+label+" ?)"
                else:
                    label = "Unknown"
                confidence = 100 - confidence
            confidence = (confidence - 50)*2
            
            face = Face(str(i) + ".png", label, confidence)

            torchvision.utils.save_image(image_data, "./out/" + str(i) + ".png")

            threshold = random.randint(0, 100)

            # PYSIGNALS
            controller.get_view().get_list_widget().add_list_requested.emit(label, confidence.__str__(), "./out/" + str(i) + ".png")
            controller.add_data_graph(label, face_data_to_process.get_time())
            i += 1