"""This is the main script file, use `python system.py` to run the software.

    Attributes:
        OUTPATH: path to save output images.
        INPATH: path to save the detected input images.
        BENCHMARCH_TIME: enable time cost tracking function.
"""
import torchvision
import sys
import threading
from threads.SharedData import SharedData
from facialDetection.webcamFDM import webcamFDM
from facialDetection.directoryFDM import directoryFDM
from userInteface.UI_Main import *
from Utilities import *
import random
import time
from superResolution.model import Generator

OUTPATH = './out'
INPATH = './input'
BENCHMARK_TIME = True

""" Sets the minimum resolution for super resolution to 64*64 """
def _main():
    """Main function, used to launch the software.
    """
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow, start)
    MainWindow.show()
    sys.exit(app.exec_())

def start(interface, inputMode):
    """Start function, linked with GUI to start threads.
    Called when detection starts.

    Args:
        interface (userInteface.UI_Main.UI_MainWindow): GUI object
        inputMode (int): choose which model to run detection. 0 for importing images, 1 for using camera.
    """
    memory.reset()
    threads = []
    detect = chooseDetectionMode(interface, inputMode)
    threads.append(detect)
    gan = threading.Thread(target = ganManager, args = [interface])
    threads.append(gan)
    recog = threading.Thread(target = recogManager, args = [interface])
    threads.append(recog)
    for thread in threads:
        thread.start()
    print("finished")

def chooseDetectionMode(interface, inputMode):
    """Used to choose which detection model to use, called by start function.

    Args:
        interface (userInteface.UI_Main.UI_MainWindow): GUI object
        inputMode (int): choose which model to run detection. 0 for importing images, 1 for using camera.
    """
    if (inputMode == 0):
        return threading.Thread(target = detectionManagerDirectory, args = [interface])
    if (inputMode == 1):
        return threading.Thread(target = detectionManagerWebcam, args = [interface])

def detectionManagerDirectory(interface):
    """Use imported image/video to detect faces.

    Args:
        interface (userInteface.UI_Main.UI_MainWindow): GUI object
    """
    print("DET: start")
    FDM = directoryFDM(interface,memory)
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

def detectionManagerWebcam(interface):
    """Use camera to record video and detect faces.

    Args:
        interface (userInteface.UI_Main.UI_MainWindow): GUI object
    """
    print("DET: start")
    FDM = webcamFDM(interface,memory)
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


def ganManager(interface):
    """ Super Resolution Section
        Checks if the image is too small (SRGAN has worse performance for  < 64bit images)
        If so apply double the size using Bicubic Interpolation
        Super Resolution is then applied
    
    Args:
        interface (userInteface.UI_Main.UI_MainWindow): GUI object
    """
    generator = Generator(4).eval()
    print("\tGAN: start")
    i = 0
    while (1):
        memory.ganQueueCount.acquire()
        if (memory.detDone.is_set() and memory.ganQueue.empty()):
            if interface.getSRGANToggleFlag():
                print("\tGAN: done")
            memory.ganDone.set()
            memory.recogQueueCount.release()
            return
        tensorToProcess = memory.ganQueue.pop()

        print("\tGAN: doing")
        if (tensorToProcess is None):
            print("\tGAN: error 0")
            return



        num_retries = 2
        for attempt_no in range(num_retries):
            try:
                if BENCHMARK_TIME:
                    start = time.time()

                if interface.getSaveImageToggleFlag():
                    torchvision.utils.save_image(tensorToProcess.clone(), "./out/" + "beforeSuperResolution" + str(i) + ".png")

                tensor = interface.srganModel.super_resolution(tensorToProcess)
  
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

        if interface.getSaveImageToggleFlag():
            torchvision.utils.save_image(normalised.clone(), "./out/" + "AfterSuperResolution" + str(i) + ".png")

        i += 1
        memory.recogQueue.push(normalised)
        memory.recogQueueCount.release()


def recogManager(interface):
    """Face recognition section, will process all pictures in recognition queue in order.

    Args:
        interface (userInteface.UI_Main.UI_MainWindow): GUI object
    """

    i = 0
    while (1):
        memory.recogQueueCount.acquire()
        if (memory.detDone.is_set() and memory.ganDone.is_set() and memory.recogQueue.empty()):
            interface.importButton.setEnabled(True)
            interface.webcamButton.setEnabled(True)
            interface.setEnabledButtons(True)
            interface.saveNameToText()
            return
            print("\t\tREC: done")
        tensor = memory.recogQueue.pop()
        print("\t\tREC: doing")
        if (tensor is None):
            print("\t\tREC: queue empty")
        else:

            try:
                if BENCHMARK_TIME:
                    start = time.time()
                confidence, label = interface.recogModel.recognize(tensor)
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

            if interface.getSaveImageToggleFlag():
                torchvision.utils.save_image(tensor, "./out/" + str(i) + ".png")

            threshold = random.randint(0, 100)
            if not interface.forImage and confidence >= threshold:
                interface.addFace(face)
            elif interface.forImage:
                interface.addFace(face)
            i += 1

if __name__ == '__main__':
    """ Makes folders """
    os.makedirs(OUTPATH, exist_ok=True)
    os.makedirs(INPATH, exist_ok=True)
    memory = SharedData()
    _main()
