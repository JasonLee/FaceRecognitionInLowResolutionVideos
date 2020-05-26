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


    def run(self, testForGAN, cv2_to_tensor):
        """ Reads frames from the image or video file loaded into the input directory and processes them.
        
            Args:
                testForGAN: function that checks if super resolution should be applied to a face.
                cv2_to_tensor: function that converts an OpenCV image into a tensor.
        """
        self.faces_counted = 0
        self.controller.get_logger_system().info("DET: using directory")
        # Files the newest file in the dir /input
        # TODO GET RID OF USING INPUT
        file = os.listdir(self.indir)[0]
        self.controller.get_logger_system().info("DET: found " + file)
        if file.endswith('.png') or file.endswith('.jpg'):
            self.controller.get_logger_system().info("Processing single image")
            cv2_image = cv2.imread(self.indir + "/" + file)
            self.setFrame(cv2_image)
            self.locateFaces(0)
            self.processFrame(testForGAN, cv2_to_tensor)
            self.controller.get_logger_system().info("Processing single image - Done")

        elif file.endswith('.mp4'):
            self.controller.get_logger_system().info("Processing video")
            self.controller.set_video_processing_flag(True)

            cv2_video = cv2.VideoCapture(self.indir + '/' + file)

            video_writer = self.set_up_video_writer(cv2_video)

            frame_rate = cv2_video.get(cv2.CAP_PROP_FPS)
            seconds_per_frame = self.controller.get_settings().value("Video Capture FPS", 0, int)

            frame_sample = int(frame_rate) * seconds_per_frame

            success, image = cv2_video.read()

            while success and self.controller.get_video_processing_flag() is True:
                frame_count = cv2_video.get(cv2.CAP_PROP_POS_FRAMES)
                if frame_count % frame_sample == 0:
                    self.setFrame(image)
                    time_of_frame = cv2_video.get(cv2.CAP_PROP_POS_MSEC)
                    new_frame = self.locateFaces(time_of_frame)
                    video_writer.write(new_frame)
                    self.processFrame(testForGAN, cv2_to_tensor)
                success, image = cv2_video.read()

            cv2_video.release()
            video_writer.release()
            cv2.destroyAllWindows()

            self.controller.finished_video_processing()
            self.frame_counter = 0
            self.controller.set_video_processing_flag(False)

        else:
            self.controller.get_logger_system().info("DET: Error, unrecognised input file")
        self.controller.get_logger_system().info("Processing video - Done")

    def set_up_video_writer(self, cv2_video_obj):
        height = int(cv2_video_obj.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(cv2_video_obj.get(cv2.CAP_PROP_FRAME_WIDTH))
        fps_new_video = 1

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        return cv2.VideoWriter(self.outdir + '/' + "processed.mp4", fourcc, fps_new_video, (width, height))
