import time

import cv2

from facialDetection.facialDetectionManager import facialDetectionManager


class webcamFDM(facialDetectionManager):

    def __init__(self, controller, memory):
        super(webcamFDM, self).__init__(controller, memory)

    def run(self, webcam_source, testForGAN, cv2_to_tensor):
        frames_counted = 0
        frame_rate = webcam_source.get(cv2.CAP_PROP_FPS)
        # around 3 fps
        seconds_per_frame = 1 / float(self.controller.get_settings().value("Webcam FPS", "15", str))

        frame_sample = int(float(frame_rate) * seconds_per_frame)

        while self.controller.is_webcam_activated() is True:
            cv2_image = webcam_source.read()[1]
            
            time_of_frame = webcam_source.get(cv2.CAP_PROP_POS_MSEC)
            # print("time_of_frame",time_of_frame)
            new_frame = self.locateFaces(time_of_frame, cv2_image)
            self.controller.set_image_view(new_frame)

            if frames_counted % frame_sample == 0:
                self.processFrame(testForGAN, cv2_to_tensor, cv2_image)
                
            frames_counted += 1

        webcam_source.release()
        cv2.destroyAllWindows()

        self.controller.view_stop_webcam()

# Note: Video Writer functionality does work but due to limitations unknown video writing
# puts great strain on the CPU which causes the application to freeze.
