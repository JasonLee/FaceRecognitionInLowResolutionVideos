import time

import cv2

from facialDetection.facialDetectionManager import facialDetectionManager


class webcamFDM(facialDetectionManager):

    def __init__(self, controller, memory):
        super(webcamFDM, self).__init__(controller, memory)

    def run(self, webcam_source, testForGAN, cv2_to_tensor):
        frames_counted = 0
        # video_writer = self.set_up_video_writer(webcam_source, "processed_webcam.mp4")
        frame_rate = webcam_source.get(cv2.CAP_PROP_FPS)
        # around 3 fps
        seconds_per_frame = 1 / float(self.controller.get_settings().value("Webcam FPS", "15", str))

        frame_sample = int(float(frame_rate) * seconds_per_frame)

        while self.controller.is_webcam_activated() is True:
            cv2_image = webcam_source.read()[1]
            if frames_counted % frame_sample == 0:
                time_of_frame = webcam_source.get(cv2.CAP_PROP_POS_MSEC)
                new_frame = self.locateFaces(time_of_frame, cv2_image)
                # video_writer.write(new_frame)
                self.processFrame(testForGAN, cv2_to_tensor, cv2_image)
            frames_counted += 1

        # video_writer.release()
        webcam_source.release()
        cv2.destroyAllWindows()

        self.controller.view_stop_webcam()
        # self.controller.finished_video_processing("out/processed_webcam.mp4")

# Note: Video Writer functionality does work but due to limitations unknown video writing
# puts great strain on the CPU which causes the application to freeze.
