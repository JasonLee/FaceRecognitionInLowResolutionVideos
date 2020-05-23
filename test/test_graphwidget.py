import unittest
from test.DummyController import DummyController
import GUI.MainWindow

# Runs from root directory
TEST_IMAGE_PATH = "test/test_data/test_image.png"


class GraphWidgetTest(unittest.TestCase):
    """Test GraphWidget GUI"""

    def setUp(self):
        """Create GUI without the controller"""
        self.controller = DummyController()
        self.gui = GUI.MainWindow.MainWindow(self.controller)
        self.graph = self.gui.get_graph_widget()

    def test_adding_people(self):
        """Check toolbar buttons are enabled/disabled correctly"""
        self.graph.append_to_data("John", 0)
        self.graph.append_to_data("Jane", 0)
        self.graph.append_to_data("Joe", 0)
        self.graph.plot()

        # Pulls y axis labels and makes sure they match added data
        y_labels = self.graph.get_figure().axes[0].get_yaxis().get_majorticklabels()
        self.assertEqual(y_labels[0].get_text(), "John")
        self.assertEqual(y_labels[1].get_text(), "Jane")
        self.assertEqual(y_labels[2].get_text(), "Joe")

    def test_add_duplicate_no_repeat_in_graph(self):
        """Duplicates should not be added to y axis labels"""
        self.graph.append_to_data("John", 0)
        self.graph.append_to_data("John", 0)
        self.graph.append_to_data("Jane", 0)

        self.graph.plot()

        # Pulls y axis labels and makes sure they match added data
        y_labels = self.graph.get_figure().axes[0].get_yaxis().get_majorticklabels()
        self.assertEqual(y_labels[0].get_text(), "John")
        self.assertEqual(y_labels[1].get_text(), "Jane")

    def test_rest_graph(self):
        """Duplicates should not be added to y axis labels"""
        self.graph.append_to_data("John", 0)
        self.graph.append_to_data("John", 0)
        self.graph.append_to_data("Jane", 0)
        self.graph.plot()

        self.graph.reset_figure()

        self.graph.append_to_data("Reset", 0)
        self.graph.append_to_data("Graph", 0)
        self.graph.plot()

        # Pulls y axis labels and makes sure they match added data
        y_labels = self.graph.get_figure().axes[0].get_yaxis().get_majorticklabels()

        self.assertEqual(y_labels[0].get_text(), "Reset")
        self.assertEqual(y_labels[1].get_text(), "Graph")

if __name__ == '__main__':
    unittest.main()