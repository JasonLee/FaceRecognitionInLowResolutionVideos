import sys
import unittest

from PyQt5.QtWidgets import QApplication
import GUI.MainWindow


# Runs from root directory
TEST_IMAGE_PATH = "test/test_data/test_image.png"
app = QApplication(sys.argv)


class MainWindowTest(unittest.TestCase):
    """Test MainWindow GUI"""

    def setUp(self):
        """Create GUI without the controller"""

        self.gui = GUI.MainWindow.MainWindow(None)

    def test_default_toolbar(self):
        """Check toolbar buttons are enabled/disabled correctly"""
        self.assertEqual(self.gui.import_images_button.isEnabled(), True)
        self.assertEqual(self.gui.import_videos_button.isEnabled(), True)
        self.assertEqual(self.gui.webcam_button.isEnabled(), True)
        self.assertEqual(self.gui.tick_button.isEnabled(), False)
        self.assertEqual(self.gui.cross_button.isEnabled(), False)

    def test_adding_to_live_list(self):
        self.gui.get_list_widget().add_live_tab("Name", "Confidence", TEST_IMAGE_PATH)
        count = self.gui.get_list_widget().get_live_list_widget().count()
        self.assertEqual(count, 1)

        item = self.gui.get_list_widget().get_live_list_widget().item(0)
        live_result_block_data = self.gui.get_list_widget().get_live_list_widget().itemWidget(item)

        self.assertEqual(live_result_block_data.name, "Name")
        self.assertEqual(live_result_block_data.confidence, "Confidence")

    def test_setting_image_frame(self):
        self.gui.set_image_frame(TEST_IMAGE_PATH)
        image_pixmap = self.gui.image_frame_label.pixmap()

        self.assertTrue(image_pixmap is not None)


if __name__ == '__main__':
    unittest.main()