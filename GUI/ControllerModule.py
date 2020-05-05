import sys

from PyQt5.QtWidgets import QApplication

from GUI.MainWindow import MainWindow
from system import set_controller, start, add_corrected_face


class Controller:
    def __init__(self):

        app = QApplication(sys.argv)
        self.__view = MainWindow(self)
        set_controller(self)

        self.__view.show()
        app.exec()

    def image_selected(self, image_path):
        start(0)

    def webcam_activated(self):
        start(1)

    def view_stop_webcam(self):
        self.__view.reset_webcam()

    def is_webcam_activated(self):
        return self.__view.is_webcam_activated()

    def set_image_view(self, image_path):
        self.__view.set_image_frame(image_path)

    def add_data_graph(self, label):
        self.__view.get_graph_widget().append_to_data(label)
        self.__view.get_graph_widget().plot()

    def get_view(self):
        return self.__view

    def add_text(self, text):
        self.__view.text_out.append(text)

    def add_face_db(self, name, face_pixmap):
        add_corrected_face(name, face_pixmap)

