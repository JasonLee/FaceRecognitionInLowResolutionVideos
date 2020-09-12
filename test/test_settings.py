import unittest

import GUI.MainWindow
from test.DummyController import DummyController


class SettingsTest(unittest.TestCase):
    """Test Settings Dialog GUI"""

    def setUp(self):
        """Create GUI without the controller"""
        self.controller = DummyController()
        self.gui = GUI.MainWindow.MainWindow(self.controller)
        self.settings_page = self.gui.get_settings_page()

        # Default Settings:
        self.settings_page.settings.setValue("Hardware", 0)
        self.settings_page.settings.setValue("Face Detection Confidence", 0.4)
        self.settings_page.settings.setValue("Video Capture FPS", 1)
        self.settings_page.settings.setValue("Toggle SR",0)
        self.settings_page.settings.setValue("Face Recognition Minimum Confidence", 70)

    def test_options_load(self):
        self.assertEqual(self.settings_page._hardware_combo_box.isEnabled(), True)
        self.assertEqual(self.settings_page._confidence_combo_box.isEnabled(), True)
        self.assertEqual(self.settings_page._fps_combo_box.isEnabled(), True)
        self.assertEqual(self.settings_page._toggle_sr_check.isCheckable(), True)
        self.assertEqual(self.settings_page._min_combo_box.isEnabled(), True)

    def test_values_in_ini(self):
        self.assertEqual(self.settings_page.settings.value("Hardware", -1, int), 0)
        self.assertEqual(self.settings_page.settings.value("Face Detection Confidence", -1.0, float), 0.4)
        self.assertEqual(self.settings_page.settings.value("Video Capture FPS", -1, int), 1)
        self.assertEqual(self.settings_page.settings.value("Toggle SR", -1, int), 0)
        self.assertEqual(self.settings_page.settings.value("Face Recognition Minimum Confidence", -1, int), 70)

    def test_accept(self):
        self.settings_page._hardware_combo_box.setCurrentIndex(1) # GPU
        self.settings_page._confidence_combo_box.setCurrentIndex(0)
        self.settings_page._fps_combo_box.setCurrentIndex(1)
        self.settings_page._toggle_sr_check.setChecked(True)
        self.settings_page._min_combo_box.setCurrentIndex(0)

        self.settings_page.select_accept()

        self.assertEqual(self.settings_page.settings.value("Hardware", -1, int), 1)
        self.assertEqual(self.settings_page.settings.value("Face Detection Confidence", -1.0, float), 0.2)
        self.assertEqual(self.settings_page.settings.value("Video Capture FPS", -1, int), 1)
        self.assertEqual(self.settings_page.settings.value("Toggle SR", -1, int), 2)
        self.assertEqual(self.settings_page.settings.value("Face Recognition Minimum Confidence", -1, int), 50)

    def test_reject(self):
        self.settings_page._hardware_combo_box.setCurrentIndex(1)  # GPU
        self.settings_page._confidence_combo_box.setCurrentIndex(0)
        self.settings_page._fps_combo_box.setCurrentIndex(0)
        self.settings_page._toggle_sr_check.setChecked(True)
        self.settings_page._min_combo_box.setCurrentIndex(0)

        self.settings_page.select_reject()

        self.assertEqual(self.settings_page.settings.value("Hardware", -1, int), 0)
        self.assertEqual(self.settings_page.settings.value("Face Detection Confidence", -1.0, float), 0.4)
        self.assertEqual(self.settings_page.settings.value("Video Capture FPS", -1, int), 1)
        self.assertEqual(self.settings_page.settings.value("Toggle SR", -1, int), 0)
        self.assertEqual(self.settings_page.settings.value("Face Recognition Minimum Confidence", -1, int), 70)






