import unittest

import GUI.MainWindow

# Runs from root directory
TEST_IMAGE_PATH = "test/test_data/test_image.png"


class VideoPlayerTest(unittest.TestCase):
    """Test GraphWidget GUI"""

    def setUp(self):
        """Create GUI without the controller"""
        self.gui = GUI.MainWindow.MainWindow(None)
        self.video_player = self.gui.get_video_player()

    def test_default_toolbar(self):
        """Check toolbar buttons are enabled/disabled correctly"""
        self.assertEqual(self.video_player.play_button.isEnabled(), True)
        self.assertEqual(self.video_player.process_button.isEnabled(), True)

    # TODO: Figure out a way to store video test data and test the media player.
    #  Potentially find some copyright free stock videos as test data.
