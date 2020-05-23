from PyQt5.QtCore import QSettings

TEST_SETTINGS_PATH = "test/test_data/test_settings.ini"


class DummyController:
    def __init__(self):
        self._settings = QSettings(TEST_SETTINGS_PATH, QSettings.IniFormat)

    def get_settings(self):
        return self._settings

