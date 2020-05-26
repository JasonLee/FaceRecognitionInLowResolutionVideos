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
        frame_rate = cam.get(cv2.CAP_PROP_FPS)
        self.controller.get_logger_system().info("frame_rate - ", frame_rate)
        # around 3 fps
        seconds_per_frame = 1/3

        frame_sample = int(float(frame_rate) * seconds_per_frame)

        while self.controller.is_webcam_activated() is True:
            cv2_image = cam.read()[1]
            if self.frames_counted % frame_sample == 0:
                time_of_frame = cam.get(cv2.CAP_PROP_POS_MSEC)
                self.setFrame(cv2_image)
                self.locateFaces(time_of_frame)
                self.choose_face()
                self.processFrame(testForGAN, cv2_to_tensor)
            self.frames_counted += 1

        self.controller.view_stop_webcam()
        cam.release()  # Attempt to Kill the webcam, DOESN@T SEEM TO WORK
        cv2.destroyAllWindows()

    def choose_face(self):
        """temporary fix to achieve real time recognition: reduces a face list of length=n from a frame to a list of length=1"""
        num_of_faces_found = len(self.faces)
        if num_of_faces_found > 1:
            self.chosen_face = (self.chosen_face + 1) % num_of_faces_found
            self.faces = [ self.faces[self.chosen_face] ]
