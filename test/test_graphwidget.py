import sys
import unittest

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
import GUI.MainWindow
app = QApplication(sys.argv)

# Runs from root directory
TEST_IMAGE_PATH = "test/test_data/test_image.png"


class GraphWidgetTest(unittest.TestCase):
    """Test GraphWidget GUI"""

    def setUp(self):
        """Create GUI without the controller"""
        self.gui = GUI.MainWindow.MainWindow(None)
        self.graph = self.gui.get_graph_widget()

    def test_adding_people(self):
        """Check toolbar buttons are enabled/disabled correctly"""
        self.graph.append_to_data("John")
        self.graph.append_to_data("Jane")
        self.graph.append_to_data("Joe")
        self.graph.plot()

        # Pulls y axis labels and makes sure they match added data
        y_labels = self.graph.get_figure().axes[0].get_yaxis().get_majorticklabels()
        self.assertEqual(y_labels[0].get_text(), "John")
        self.assertEqual(y_labels[1].get_text(), "Jane")
        self.assertEqual(y_labels[2].get_text(), "Joe")

    def test_add_duplicate_no_repeat_in_graph(self):
        """Duplicates should not be added to y axis labels"""
        self.graph.append_to_data("John")
        self.graph.append_to_data("John")
        self.graph.append_to_data("Jane")

        self.graph.plot()

        # Pulls y axis labels and makes sure they match added data
        y_labels = self.graph.get_figure().axes[0].get_yaxis().get_majorticklabels()
        self.assertEqual(y_labels[0].get_text(), "John")
        self.assertEqual(y_labels[1].get_text(), "Jane")

    def test_rest_graph(self):
        """Duplicates should not be added to y axis labels"""
        self.graph.append_to_data("John")
        self.graph.append_to_data("John")
        self.graph.append_to_data("Jane")
        self.graph.plot()

        self.graph.reset_figure()

        self.graph.append_to_data("Reset")
        self.graph.append_to_data("Graph")
        self.graph.plot()

        # Pulls y axis labels and makes sure they match added data
        y_labels = self.graph.get_figure().axes[0].get_yaxis().get_majorticklabels()

        self.assertEqual(y_labels[0].get_text(), "Reset")
        self.assertEqual(y_labels[1].get_text(), "Graph")


if __name__ == '__main__':
    unittest.main()