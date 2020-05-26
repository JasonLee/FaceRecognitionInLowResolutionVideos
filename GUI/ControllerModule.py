import sys
import logging

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication

from GUI.MainWindow import MainWindow
from system import set_controller, start, add_corrected_face


class Controller:
    def __init__(self):

        app = QApplication(sys.argv)
        self._settings = QSettings('settings.ini', QSettings.IniFormat)

        self._logger_gui = self.setup_logger("MainGUI")
        self._logger_controller = self.setup_logger("Controller")
        self._logger_system = self.setup_logger("System")

        self.__view = MainWindow(self)

        set_controller(self)

        self.__view.show()
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
        self._logger_controller.info("Starting processing mage")
        start(0)

    def webcam_activated(self):
        self._logger_controller.info("Starting processing video")
        start(1)

    def view_stop_webcam(self):
        self._logger_controller.info("Stop webcam")
        self.__view.reset_webcam()

    def is_webcam_activated(self):
        return self.__view.is_webcam_activated()

    def set_image_view(self, image_path):
        self._logger_controller.info("Set view processed image")
        # Image View
        if self.__view.get_status() == 0:
            self.__view.set_image_frame(image_path)
        else:
            self.__view.set_video_processing_frame(image_path)

    def add_data_graph(self, label, time):
        self._logger_controller.info("Add data to graph")
        self.__view.get_graph_widget().append_to_data(label, time)
        self.__view.get_graph_widget().plot()

    def get_view(self):
        return self.__view

    def add_text(self, text):
        self.__view.text_out.append(text)

    def add_face_db(self, name, face_pixmap):
        self._logger_controller.info("Create/Add face to folder for Recognition")
        add_corrected_face(name, face_pixmap)

    def get_current_mode(self):
        # 0 is Image / 1 is View
        return self.__view.get_status()

    def finished_video_processing(self):
        self._logger_controller.info("Set processed video to video player")
        self.__view.video_display_widget.setCurrentIndex(0)
        self.__view.get_video_player().set_video("out/processed.mp4")

    def empty_all_queues(self):
        pass

    def set_video_processing_flag(self, flag):
        self.__view.is_processing_video = flag

    def get_video_processing_flag(self):
        return self.__view.is_processing_video

    def get_settings(self):
        return self._settings

    def get_logger_gui(self):
        return self._logger_gui

    def get_logger_controller(self):
        return self._logger_controller

    def get_logger_system(self):
        return self._logger_system



