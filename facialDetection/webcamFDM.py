import cv2, os
from facialDetection.facialDetectionManager import facialDetectionManager

class webcamFDM(facialDetectionManager):
    """This class applies face detection to frames obtained through a webcam.

    Args:
        interface: user interface object, QtWidgets.QMainWindow
        memory: data map, check threads.SharedData
    
    Attributes:
        faces_couted (int): the faces has been detected
        frames_counted (int): the frames has been processed

    """
    def __init__(self,controller,memory):
        super(webcamFDM,self).__init__(controller,memory)

    def run(self, cam, testForGAN, cv2_to_tensor):
        """ Reads frames from the given camera and processes them.

        Args:
            cam: an OpenCV VideoCapture device
            testForGAN: function that checks if super resolution should be applied to a face.
            cv2_to_tensor: function that converts an OpenCV image into a tensor.
        """
        self.faces_counted = 0
        self.frames_counted = 0
        self.chosen_face = 0
        count = 0

        while self.controller.is_webcam_activated() is True:
            cv2_image = cam.read()[1]
            print("DET: got image")
            self.setFrame(cv2_image)
            self.locateFaces()
            if self.shouldProcessFrame():
                self.choose_face()
                self.processFrame(testForGAN, cv2_to_tensor)
            self.frames_counted += 1

        self.controller.view_stop_webcam()
        cam.release()  # Attempt to Kill the webcam, DOESN@T SEEM TO WORK

    def choose_face(self):
        """temporary fix to achieve real time recognition: reduces a face list of length=n from a frame to a list of length=1"""
        num_of_faces_found = len(self.faces)
        if num_of_faces_found > 1:
            self.chosen_face = (self.chosen_face + 1) % num_of_faces_found
            self.faces = [ self.faces[self.chosen_face] ]
