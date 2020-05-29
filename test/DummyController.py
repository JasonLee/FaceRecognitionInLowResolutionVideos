from PyQt5.QtCore import QSettings
import logging

TEST_SETTINGS_PATH = "test/test_data/test_settings.ini"


class DummyController:
    def __init__(self):
        self._settings = QSettings(TEST_SETTINGS_PATH, QSettings.IniFormat)
        self._logger_gui = self.setup_logger("MainGUI")
        self._logger_controller = self.setup_logger("Controller")
        self._logger_system = self.setup_logger("System")

    def setup_logger(self, logger_name):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARN)
        # create file handler which logs even debug messages
        fh = logging.FileHandler('logging/general.log')
        fh.setLevel(logging.WARN)
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

    def get_settings(self):
        return self._settings

    def get_logger_gui(self):
        return self._logger_gui

    def get_logger_controller(self):
        return self._logger_controller

    def get_logger_system(self):
        return self._logger_system

