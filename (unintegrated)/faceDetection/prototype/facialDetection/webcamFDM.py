import cv2, os
from .facialDetectionManager import facialDetectionManager

INPATH = './input'

class webcamFDM(facialDetectionManager):
    """performs facial detection on a webcam stream"""

    def run(self, cam):
        """reads a frame from the given webcam"""
        cv2_image = cam.read()[1]
        print("DET: got image")
        cv2.imwrite(os.path.join(INPATH, 'webcam.jpg'), cv2_image)
        self.setFrame(cv2_image)
        self.locateFaces()
