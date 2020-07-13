import logging
import sys

import cv2
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication

from GUI.MainWindow import MainWindow
from system import set_controller, start, add_corrected_face, update_rec_baseline
from database.database import init_database


IMAGE_VIEW = 0
VIDEO_VIEW = 1


class Controller:
    def __init__(self):
        # Create application
        app = QApplication(sys.argv)
        self._settings = QSettings('settings.ini', QSettings.IniFormat)
        self.current_video_cv2 = None
        self.path_to_file = ""

        self._logger_gui = self.setup_logger("MainGUI")
        self._logger_controller = self.setup_logger("Controller")
        self._logger_system = self.setup_logger("System")

        # Setup Database
        init_database(self)

        # Setup pytorch models and threads
        set_controller(self)

        self._view = MainWindow(self)

        self._view.show()
        app.exec()

    def setup_logger(self, logger_name):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        fh = logging.FileHandler('logging/general.log')
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger

    def image_selected(self):
        """ Start Face detection on image """
        self._logger_controller.info("Starting processing image")
        start(0)

    def webcam_activated(self):
        """ Start face detection on web cam feed """
        self._logger_controller.info("Starting processing video")
        start(1)

    def view_stop_webcam(self):
        self._logger_controller.info("Stop webcam")
        self._view.reset_frame()

    def is_webcam_activated(self):
        return self._view.is_webcam_activated()

    def set_image_view(self, image_path):
        self._logger_controller.info("Set view processed image")
        # Image View
        if self._view.get_status() == 0:
            self._view.set_image_frame(image_path)
        else:
            self._view.set_video_processing_frame(image_path)

    def add_data_graph(self, label, time):
        self._logger_controller.info("Add data to graph")
        self._view.get_graph_widget().append_to_data(label, time)
        self._view.get_graph_widget().plot()

    def add_face_db(self, name, face_pixmap):
        self._logger_controller.info("Add face to DB for Recognition")
        add_corrected_face(name, face_pixmap)

    def finished_video_processing(self, path):
        self._logger_controller.info("Set processed video to video player")
        self._view.video_display_widget.setCurrentIndex(0)
        self._view.image_video_view.setCurrentIndex(1)
        self._view.get_video_player().set_video(path)
        self._view.get_video_player().process_button.setDisabled(True)

    def set_video_processing_flag(self, flag):
        self._view.is_processing_video = flag

    def set_current_video_cv2(self, current_video_path):
        if current_video_path is None:
            self.current_video_cv2.release()
            self.current_video_cv2 = None
            return

        self.current_video_cv2 = cv2.VideoCapture(current_video_path)
        if self.current_video_cv2 is None:
            self.get_logger_gui().error("Can't get VideoCapture")

    def set_disabled_cross_button(self, bool):
        self._view.cross_button.setDisabled(bool)

    def set_file_path(self, file):
        self.path_to_file = file

    def get_current_video_cv2(self):
        return self.current_video_cv2

    def get_file_path(self):
        return self.path_to_file

    def get_current_mode(self):
        # 0 is Image / 1 is View
        return self._view.get_status()

    def get_video_processing_flag(self):
        return self._view.is_processing_video

    def get_settings(self):
        return self._settings

    def get_view(self):
        return self._view

    def get_logger_gui(self):
        return self._logger_gui

    def get_logger_controller(self):
        return self._logger_controller

    def get_logger_system(self):
        return self._logger_system

    def update_rec_model(self):
        update_rec_baseline()
