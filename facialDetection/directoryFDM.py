import cv2
import os

from facialDetection.facialDetectionManager import facialDetectionManager


class directoryFDM(facialDetectionManager):

    def __init__(self, controller, memory):
        super(directoryFDM, self).__init__(controller, memory)

    def run(self, testForGAN, cv2_to_tensor):
        """ Reads frames from the image or video file loaded into the input directory and processes them.
        
            Args:
                testForGAN: function that checks if super resolution should be applied to a face.
                cv2_to_tensor: function that converts an OpenCV image into a tensor.
        """
        self.controller.get_logger_system().info("DET: using directory")
        # Files the newest file in the dir /input
        # TODO GET RID OF USING INPUT
        file = self.controller.get_file_path()


        self.controller.get_logger_system().info("DET: found " + file)

        if file.endswith('.png') or file.endswith('.jpg'):
            self.controller.get_logger_system().info("Processing single image")
            cv2_image = cv2.imread(file)
            boxedFaces = self.locateFaces(0, cv2_image)
            self.controller.set_image_view(boxedFaces)
            self.processFrame(testForGAN, cv2_to_tensor, cv2_image)
            self.controller.get_logger_system().info("Processing single image - Done")

        elif file.endswith('.mp4'):
            self.controller.get_logger_system().info("Processing video")
            self.controller.set_video_processing_flag(True)

            cv2_video = cv2.VideoCapture(file)

            frame_rate = cv2_video.get(cv2.CAP_PROP_FPS)
            seconds_per_frame = self.controller.get_settings().value("Video Capture FPS", 0, int)

            frame_sample = int(frame_rate) * seconds_per_frame

            success, image = cv2_video.read()

            while cv2_video.isOpened() and success and self.controller.get_video_processing_flag() is True:
                frame_count = cv2_video.get(cv2.CAP_PROP_POS_FRAMES)

                time_of_frame = cv2_video.get(cv2.CAP_PROP_POS_MSEC)
                new_frame = self.locateFaces(time_of_frame, image)
                self.controller.set_image_view(new_frame)

                if frame_count % frame_sample == 0:
                    self.processFrame(testForGAN, cv2_to_tensor, image)


                success, image = cv2_video.read()

            self.controller.set_video_processing_flag(False)

            cv2_video.release()
            cv2.destroyAllWindows()

            self.controller.finished_video_processing(file)
            

        else:
            self.controller.get_logger_system().info("DET: Error, un-recognised input file")
        self.controller.get_logger_system().info("Processing video - Done")
# 