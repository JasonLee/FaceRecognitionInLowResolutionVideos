import cv2, os
from facialDetection.facialDetectionManager import facialDetectionManager

class directoryFDM(facialDetectionManager):
    """This class applies face detection to frames obtained through a webcam.

    Args:
        interface: user interface object, QtWidgets.QMainWindow
        memory: data map, check threads.SharedData
    
    Attributes:
        faces_couted (int): the faces has been detected
        frames_counted (int): the frames has been processed
        indir (str): the input directory.
    """
    def __init__(self, controller, memory):
        super(directoryFDM,self).__init__(controller, memory)
        self.indir = 'input'
        self.isDirectory = True


    def run(self, testForGAN, cv2_to_tensor):
        """ Reads frames from the image or video file loaded into the input directory and processes them.
        
            Args:
                testForGAN: function that checks if super resolution should be applied to a face.
                cv2_to_tensor: function that converts an OpenCV image into a tensor.
        """
        self.faces_counted = 0
        self.frames_counted = 0
        print("DET: using directory")
        file = os.listdir(self.indir)[0]
        print("DET: found " + file)
        if file.endswith('.png') or file.endswith('.jpg'):
            cv2_image = cv2.imread(self.indir+"/"+file)
            self.setFrame(cv2_image)
            self.locateFaces()
            self.processFrame(testForGAN, cv2_to_tensor)
        elif file.endswith('.mp4'):
            cv2_video = cv2.VideoCapture(self.indir+'/'+file)
            success, image = cv2_video.read()
            while success:
                self.setFrame(image)
                self.locateFaces()
                if self.shouldProcessFrame():
                    self.processFrame(testForGAN, cv2_to_tensor)
                self.frames_counted += 1
                success, image = cv2_video.read()

        else:
            print("DET: Error, unrecognised input file")


