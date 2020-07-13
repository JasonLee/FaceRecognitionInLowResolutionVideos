from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import datetime as dt
import matplotlib.dates as mdates
from matplotlib.collections import PolyCollection
from random import randrange


class GraphWidget(QWidget):

    def __init__(self, controller):
        super(GraphWidget, self).__init__()
        self.controller = controller

        # figure instance to plot on
        self._figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self._figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self._raw_data = []
        self._face_labels = []
        # Maps 3rd column to y axis
        self._y_labels = {}
        self._colour_mapper = {}

        self._processed_bars = []
        self._processed_colour_mapping = []

    def plot(self):
        """ Plot data on figure to display"""
        verts = []
        colors = []

        if not self._raw_data:
            self.canvas.draw()
            return

        for d in self._raw_data:
            v = [(mdates.date2num(d[0]), self._y_labels[d[2]] - 0.4),  # 0.4 is width /2 so width of each bar is 0.8
                 (mdates.date2num(d[0]), self._y_labels[d[2]] + 0.4),
                 (mdates.date2num(d[1]), self._y_labels[d[2]] + 0.4),
                 (mdates.date2num(d[1]), self._y_labels[d[2]] - 0.4)]
            verts.append(v)  # Add bar dimensions to list
            colors.append(self._colour_mapper[d[2]])  # Assign colors to bars

        bars = PolyCollection(verts, facecolors=colors)

        self._ax = self._figure.add_subplot(111)
        self._ax.add_collection(bars)
        self._ax.autoscale()

        loc = mdates.AutoDateLocator()

        self._ax.xaxis.set_major_locator(loc)
        self._ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(loc))

        self._ax.set_yticks(range(1, len(self._y_labels.keys()) + 1))
        self._ax.set_yticklabels(self._face_labels)

        self.canvas.draw()
        self.controller.get_logger_gui().info("Plot Graph")

    def append_to_data(self, face_label, time):
        """ Reformat data to add to array to be displayed"""
        base_time = dt.datetime(2020, 1, 1, 0, 0)

        offset_time = base_time + dt.timedelta(milliseconds=time)
        formatted_data = (offset_time, offset_time + dt.timedelta(seconds=1), face_label)

        if face_label not in self._y_labels:
            self._y_labels[face_label] = len(self._y_labels.keys()) + 1
            self._face_labels.append(face_label)
            self._colour_mapper[face_label] = "C" + randrange(10).__str__()

        self._raw_data.append(formatted_data)

    def get_figure(self):
        return self._figure

    def reset_figure(self):
        self._figure.clear()
        self._raw_data = []
        self._face_labels = []
        # Maps 3rd column to y axis
        self._y_labels = {}
        self._colour_mapper = {}

        self._processed_bars = []
        self._processed_colour_mapping = []
        self.plot()
