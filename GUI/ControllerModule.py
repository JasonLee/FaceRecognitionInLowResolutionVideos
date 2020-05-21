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

    def image_selected(self):
        start(0)

    def webcam_activated(self):
        start(1)

    def view_stop_webcam(self):
        self.__view.reset_webcam()

    def is_webcam_activated(self):
        return self.__view.is_webcam_activated()

    def set_image_view(self, image_path):
        # Image View
        if self.__view.get_status() == 0:
            self.__view.set_image_frame(image_path)
        else:
            self.__view.set_video_processing_frame(image_path)

    def add_data_graph(self, label, time):
        self.__view.get_graph_widget().append_to_data(label, time)
        self.__view.get_graph_widget().plot()

    def get_view(self):
        return self.__view

    def add_text(self, text):
        self.__view.text_out.append(text)

    def add_face_db(self, name, face_pixmap):
        add_corrected_face(name, face_pixmap)

    def get_current_mode(self):
        # 0 is Image / 1 is View
        return self.__view.get_status()

    def finished_video_processing(self):
        self.__view.video_display_widget.setCurrentIndex(0)
        self.__view.get_video_player().set_video("out/processed.mp4")

    def empty_all_queues(self):
        pass

    def set_video_processing_flag(self, flag):
        self.__view.is_processing_video = flag

    def get_video_processing_flag(self):
        return self.__view.is_processing_video




