import time

import cv2

from facialDetection.facialDetectionManager import facialDetectionManager


class webcamFDM(facialDetectionManager):

    def __init__(self, controller, memory):
        super(webcamFDM, self).__init__(controller, memory)

    def run(self, webcam_source, testForGAN, cv2_to_tensor):
        frames_counted = 0

        frame_rate = webcam_source.get(cv2.CAP_PROP_FPS)
        self.controller.get_logger_system().info("Webcam fps: " +  str(frame_rate))


        setting_fps = self.controller.get_settings().value("Webcam FPS", str(frame_rate), str)

        if setting_fps == "Webcam FPS":
            setting_fps = frame_rate
        else:
            setting_fps = int(setting_fps)

            if setting_fps != frame_rate and webcam_source.set(cv2.CAP_PROP_FPS, int(setting_fps)) == True:
                self.controller.get_logger_system().info("ATTEMPTED TO CHANGE WEBCAM FPS: SUCCESS")
                frame_rate = setting_fps
                print("Webcam fps was changed")
            else: 
                self.controller.get_logger_system().info("ATTEMPTED TO CHANGE WEBCAM FPS: FAILED")
                frame_rate = webcam_source.get(cv2.CAP_PROP_FPS)

        
        self.controller.get_logger_system().info("Webcam fps: " +  str(frame_rate))

        while self.controller.is_webcam_activated() is True:
            cv2_image = webcam_source.read()[1]
            if cv2_image is None:
                continue
            
            # webcam_source.get(cv2.CAP_PROP_POS_MSEC) can return 0 if webcam doesn't support it
            if webcam_source.get(cv2.CAP_PROP_POS_MSEC) > 0:
                time_of_frame = webcam_source.get(cv2.CAP_PROP_POS_MSEC)

                new_frame = self.locateFaces(time_of_frame, cv2_image)
            else:
                test_time = 1000.0 * float(frames_counted)/frame_rate
                new_frame = self.locateFaces(test_time, cv2_image)

            self.controller.set_image_view(new_frame)

            self.processFrame(testForGAN, cv2_to_tensor, cv2_image)
                
            frames_counted += 1

        webcam_source.release()
        cv2.destroyAllWindows()

        self.controller.view_stop_webcam()

# Note: Video Writer functionality does work but due to limitations unknown video writing
# puts great strain on the CPU which causes the application to freeze.
