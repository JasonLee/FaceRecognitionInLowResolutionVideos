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

        #figure instance to plot on
        self.__figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.__figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.__raw_data = []
        self.__face_labels = []
        # Maps 3rd column to y axis
        self.__y_labels = {}
        self.__colour_mapper = {}

        self.__processed_bars = []
        self.__processed_colour_mapping = []

    def plot(self):
        verts = []
        colors = []

        if not self.__raw_data:
            self.canvas.draw()
            return

        for d in self.__raw_data:
            v = [(mdates.date2num(d[0]), self.__y_labels[d[2]] - 0.4),  # 0.4 is width /2 so width of each bar is 0.8
                 (mdates.date2num(d[0]), self.__y_labels[d[2]] + 0.4),
                 (mdates.date2num(d[1]), self.__y_labels[d[2]] + 0.4),
                 (mdates.date2num(d[1]), self.__y_labels[d[2]] - 0.4)]
            verts.append(v)  # Add bar dimensions to list
            colors.append(self.__colour_mapper[d[2]])  # Assign colors to bars

        bars = PolyCollection(verts, facecolors=colors)

        self.__ax = self.__figure.add_subplot(111)
        self.__ax.add_collection(bars)
        self.__ax.autoscale()

        loc = mdates.AutoDateLocator()

        self.__ax.xaxis.set_major_locator(loc)
        self.__ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(loc))

        self.__ax.set_yticks(range(1, len(self.__y_labels.keys()) + 1))
        self.__ax.set_yticklabels(self.__face_labels)

        self.canvas.draw()
        self.controller.get_logger_gui().info("Plot Graph")

    def append_to_data(self, face_label, time):
        base_time = dt.datetime(2020, 1, 1, 0, 0)

        offset_time = base_time + dt.timedelta(milliseconds=time)
        formatted_data = (offset_time, offset_time + dt.timedelta(seconds=1), face_label)

        if face_label not in self.__y_labels:
            self.__y_labels[face_label] = len(self.__y_labels.keys()) + 1
            self.__face_labels.append(face_label)
            self.__colour_mapper[face_label] = "C" + randrange(10).__str__()

        self.__raw_data.append(formatted_data)

    def get_figure(self):
        return self.__figure

    def reset_figure(self):
        self.__figure.clear()
        self.__raw_data = []
        self.__face_labels = []
        # Maps 3rd column to y axis
        self.__y_labels = {}
        self.__colour_mapper = {}

        self.__processed_bars = []
        self.__processed_colour_mapping = []
        self.plot()






