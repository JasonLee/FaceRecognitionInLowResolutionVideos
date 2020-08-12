import os

# Fixes issue with pyinstaller thinking a pytorch library doesnt exist
os.environ["PYTORCH_JIT"] = "0"

from torchvision import transforms

import threading

from database.SharedData import SharedData
from facialDetection.webcamFDM import webcamFDM
from facialDetection.directoryFDM import directoryFDM
from Utilities import *
import time
from superResolution.Srgan_Utils import *
from FaceRec.Rec_Utils import *

OUTPATH = './out'
BENCHMARK_TIME = False

os.makedirs(OUTPATH, exist_ok=True)

controller = None

hardware = None
srganModel = None
recogModel = None
memory = None


def set_controller(control_bbj):
    global controller
    controller = control_bbj

    init_models()


def init_models():
    global hardware, srganModel, recogModel, memory

    memory = SharedData(controller)

    if controller.get_settings().value("Hardware", 0, int) == 0 and torch.cuda.is_available():
        hardware = torch.device("cuda:0")
        controller.get_logger_system().info("Hardware is GPU")
    else:
        hardware = torch.device("cpu")
        controller.get_logger_system().info("Hardware is CPU")

    controller.get_logger_system().info("Setup Hardware")

    srganModel = superResolutionModel(hardware)
    recogModel = recognitionModel(hardware)

    controller.get_logger_system().info("Setup SR and FR")


def start(inputMode):
    """Start function, linked with GUI to start threads.
    Called when detection starts.

    Args:
        inputMode (int): choose which model to run detection. 0 for importing images, 1 for using camera.
    """
    memory.reset()
    threads = []
    detect = choose_detection_mode(inputMode)
    threads.append(detect)

    if controller.get_settings().value("Toggle SR", 1, int) == 1:
        gan = threading.Thread(target=gan_manager, args=[srganModel])
        threads.append(gan)

    recog = threading.Thread(target=recog_manager, args=[recogModel, controller])
    threads.append(recog)
    for thread in threads:
        thread.start()


def choose_detection_mode(inputMode):
    """Used to choose which detection model to use, called by start function.

    Args:
        inputMode (int): choose which model to run detection. 0 for importing images, 1 for using camera.
    """
    if inputMode == 0:
        return threading.Thread(target=detection_manager_directory, args=[controller])
    if inputMode == 1:
        return threading.Thread(target=detection_manager_webcam, args=[controller])


def detection_manager_directory(controller):
    """Use imported image/video to detect faces."""
    controller.get_logger_system().info("DET: start")
    FDM = directoryFDM(controller, memory)

    if BENCHMARK_TIME:
        start = time.time()

    FDM.run(test_for_gan, cv2_to_tensor)

    if BENCHMARK_TIME:
        elapsed = (time.time() - start)
        print('FACE DETECTION: ' + str(elapsed) + 's')

    memory.detDone.set()

    if controller.get_settings().value("Toggle SR", 1, int) == 1:
        memory.ganQueueCount.release()

    memory.recogQueueCount.release()
    controller.get_logger_system().info("DET: done")
    return


def add_corrected_face(name, face):
    recogModel.add_face(name, face)


def update_rec_baseline():
    recogModel.update_base_line()


def detection_manager_webcam(controller):
    """Use camera to record video and detect faces."""
    controller.get_logger_system().info("DET: start")
    FDM = webcamFDM(controller, memory)
    CAM = cv2.VideoCapture(0)

    try:
        if BENCHMARK_TIME:
            start = time.time()

        FDM.run(CAM, test_for_gan, cv2_to_tensor)

        if BENCHMARK_TIME:
            elapsed = (time.time() - start)
            print('FACE DETECTION WEBCAM: ' + str(elapsed) + 'ns')

    except RuntimeError:
        controller.get_logger_system().error("Detection Error")
        raise

    memory.detDone.set()

    if controller.get_settings().value("Toggle SR", 1, int) == 1:
        memory.ganQueueCount.release()

    memory.recogQueueCount.release()
    controller.get_logger_system().info("DET: done")
    return


def gan_manager(srgan_model):
    """ Super Resolution Thread """

    controller.get_logger_system().info("GAN: start")
    i = 0
    while True:
        memory.ganQueueCount.acquire()
        if memory.detDone.is_set() and memory.ganQueue.empty():
            controller.get_logger_system().info("GAN: Done")
            memory.ganDone.set()
            memory.recogQueueCount.release()
            return

        face_data_to_process = memory.ganQueue.pop()

        if face_data_to_process is None:
            controller.get_logger_system().error("GAN Error")
            return

        num_retries = 1
        for attempt_no in range(num_retries):
            try:
                if BENCHMARK_TIME:
                    start = time.time()

                image_data = face_data_to_process.get_data()

                tensor = srgan_model.super_resolution(image_data)

                if BENCHMARK_TIME:
                    elapsed = (time.time() - start)
                    print('\tSUPER RESOLUTION: ' + str(elapsed) + 's')
                break
            except RuntimeError as err:
                controller.get_logger_system().error("Error: Out of Memory")
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                controller.get_logger_system().error(err)
                raise err

        # shift the image to the range (0, 1), by subtracting the minimum and dividing by the maximum pixel value range.
        min_v = torch.min(tensor)
        range_v = torch.max(tensor) - min_v
        if range_v > 0:
            normalised = (tensor - min_v) / range_v
        else:
            normalised = torch.zeros(tensor.size())
            
        i += 1
        face_data_to_process.set_data(normalised)
        memory.recogQueue.put(face_data_to_process)
        memory.recogQueueCount.release()


def recog_manager(recogModel, controller):
    """Face recognition thread, will process all pictures in recognition queue in order."""

    while True:
        memory.recogQueueCount.acquire()
        if memory.detDone.is_set() and memory.recogQueue.empty():
            if controller.get_settings().value("Toggle SR", 1, int) == 1 and not memory.ganDone.is_set():
                pass
            controller.get_logger_system().info("REC: Done")

            controller.get_view().get_list_widget().enable_all_modify_button()
            return

        face_data_to_process = memory.recogQueue.get()

        controller.get_logger_system().info("REC: doing")
        if face_data_to_process is None:
            controller.get_logger_system().info("REC: queue empty")
        else:
            try:
                if BENCHMARK_TIME:
                    start = time.time()

                image_data = face_data_to_process.get_data()
                confidence, label = recogModel.recognize(image_data)

                if BENCHMARK_TIME:
                    elapsed = (time.time() - start)
                    controller.get_logger_system().info('Face Recognition: ' + str(elapsed) + 's')
                    controller.get_logger_system().info('Name: ' + label + ", Confidence: " + str(confidence))
            except RuntimeError:
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                controller.get_logger_system().error("Face Recognition has crashed. Likely due to CUDA")
                raise

            if confidence <= controller.get_settings().value("Face Recognition Minimum Confidence", 70, int):
                if confidence >= 50:
                    label = "Unknown (" + label + " ?)"
                else:
                    label = "Unknown"
            
            image = transforms.ToPILImage()(image_data.squeeze(0))

            # PYSIGNALS
            controller.get_view().get_list_widget().add_list_requested.emit(label, confidence.__str__(), image)
            controller.add_data_graph(label, face_data_to_process.get_time())

                
