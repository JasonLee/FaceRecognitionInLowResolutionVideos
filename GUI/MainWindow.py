import os
import shutil
import sys

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMenuBar, QAction, QHBoxLayout, QWidget, QSplitter, \
    QTextEdit, QVBoxLayout, QTabWidget, QListWidget, QListWidgetItem, QFileDialog, QPushButton, QInputDialog, QLineEdit

from GUI.GraphWidget import GraphWidget

INPATH = 'input'
OUTPATH = 'out'
SELFPATH = '../userInteface'

ICON_IMAGE_PATH = 'resources/'


class MainWindow(QMainWindow):
    def __init__(self, controller, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        #  self.setStyleSheet("background-color: rgb(255,255,255); margin:5px; border:1px solid rgb(0, 0, 0); ")
        self.setWindowTitle("Face Recognition in Low Resolution Videos")
        self.resize(1200, 800)

        self.controller = controller

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.__right_widget = RightWidget(controller)

        self.__setup_menu_bar()
        self.__setup_toolbar()
        self.__setup_layout()

        self.is_webcam_active = False

    def __setup_menu_bar(self):
        self.menu_bar = QMenuBar()

        def action_mapper(action_name, function_to_connect):
            new_action = QAction(action_name, self)
            new_action.triggered.connect(function_to_connect)
            return new_action

        self.file_menu = self.menu_bar.addMenu('File')
        self.menu_bar.addAction(action_mapper('exit', self.close))
        self.file_menu.addAction(action_mapper('print', self.print_test))
        self.file_menu.addAction(action_mapper('Import Images', self.__import_image_func))
        self.file_menu.addAction(action_mapper('Import Videos', self.__import_video_func))
        self.file_menu.addAction(action_mapper('Use Webcam Feed', self.__use_webcam_func))

        self.setMenuBar(self.menu_bar)

    def __setup_toolbar(self):
        self.toolbar = self.addToolBar("Main")

        def icon_action_mapper(icon_path, action_name, function_to_connect, tooltip):
            new_action = QAction(QIcon(icon_path), action_name, self)
            new_action.triggered.connect(function_to_connect)
            new_action.setToolTip(tooltip)
            return new_action

        self.import_images_button = icon_action_mapper(
            ICON_IMAGE_PATH + "camera_icon.png", "new", self.__import_image_func, "Import Images")
        self.import_videos_button = icon_action_mapper(
            ICON_IMAGE_PATH + "video_camera_icon.png", "new", self.__import_video_func, "Import Videos")
        self.webcam_button = icon_action_mapper(
            ICON_IMAGE_PATH + "webcam_icon.png", "new", self.__use_webcam_func, "Use Webcam feed")

        self.tick_button = icon_action_mapper(
            ICON_IMAGE_PATH + "tick_icon.png", "new", self.__tick_func, "???")
        self.tick_button.setDisabled(True)

        self.cross_button = icon_action_mapper(
            ICON_IMAGE_PATH + "cross_icon.png", "new", self.__cross_func, "Cancel current event")
        self.cross_button.setDisabled(True)

        self.toolbar.addAction(self.import_images_button)
        self.toolbar.addAction(self.import_videos_button)
        self.toolbar.addAction(self.webcam_button)

        self.toolbar.addSeparator()
        self.toolbar.addAction(self.tick_button)
        self.toolbar.addAction(self.cross_button)

    def __setup_layout(self):
        layout = QHBoxLayout()

        self.image_frame_label = QLabel(self)

        # Graph placeholder
        self.__graph_widget = GraphWidget(self.controller)

        splitter_h = QSplitter(Qt.Horizontal)
        splitter_h.addWidget(self.image_frame_label)

        splitter_h.addWidget(self.__right_widget)
        splitter_h.setSizes([600, 600])

        splitter_v = QSplitter(Qt.Vertical)
        splitter_v.addWidget(splitter_h)
        splitter_v.addWidget(self.__graph_widget)
        splitter_v.setSizes([800, 600])

        layout.addWidget(splitter_v)

        self.main_widget.setLayout(layout)

    def __import_image_func(self):

        file_path, _ = QFileDialog.getOpenFileName(self, "Open File (*.jpg) (*.png)", "C:", "Images(*.jpg *.png)")

        if len(file_path) > 0:
            self.reset_folders_lists()
            shutil.copy(file_path, INPATH)
            file_name = file_path[0]
            self.__start_detection(file_name)

    def __import_video_func(self):

        file_path, _ = QFileDialog.getOpenFileName(self, "Open File (*.mp4)", "C:", "Video Files (*.mp4)")

        if len(file_path) > 0:
            self.reset_folders_lists()
            shutil.copy(file_path, INPATH)
            file_name = file_path[0]
            self.__start_detection(file_name)

    def __use_webcam_func(self):
        self.cross_button.setDisabled(False)
        self.is_webcam_active = True
        self.reset_folders_lists()
        self.controller.webcam_activated()

    # Do as required
    def __tick_func(self):
       pass

    # Do as required
    def __cross_func(self):
        if self.is_webcam_active is True:
            self.is_webcam_active = False

    def is_webcam_activated(self):
        return self.is_webcam_active

    def reset_webcam(self):
        self.cross_button.setDisabled(True)
        self.clear_image_frame()

    def __start_detection(self, file_name):
        _file_name = os.path.join(INPATH, file_name)
        self.set_image_frame(file_name)
        self.controller.image_selected(file_name)

    def set_image_frame(self, image_name):
        w = self.image_frame_label.width()
        h = self.image_frame_label.height()

        pixmap = QPixmap(image_name)
        self.image_frame_label.setPixmap(pixmap.scaled(w, h, Qt.KeepAspectRatio))

    def clear_image_frame(self):
        self.image_frame_label.clear()

    def get_right_widget(self):
        return self.__right_widget

    def get_graph_widget(self):
        return self.__graph_widget

    def reset_folders_lists(self):
        for f in os.listdir(INPATH):
            file_path = os.path.join(INPATH, f)
            os.unlink(file_path)
        for f in os.listdir(OUTPATH):
            file_path = os.path.join(OUTPATH, f)
            os.unlink(file_path)

        self.get_right_widget().get_live_list_widget().clear()
        self.get_graph_widget().reset_figure()

    def print_test(self):
        print("TEST")


class RightWidget(QWidget):
    add_list_requested = pyqtSignal(str, str, str)

    def __init__(self, controller):
        super(RightWidget, self).__init__()
        self.controller = controller
        self.layout = QVBoxLayout()

        self.setLayout(self.layout)
        self.add_list_requested.connect(self.add_live_tab)
        self.__setup_tabs()

    def __setup_tabs(self):
        self.tabs = QTabWidget()
        self.tab1_live = QListWidget()
        self.tab2_total = QListWidget()

        self.tabs.addTab(self.tab1_live, "Live Results")
        self.tabs.addTab(self.tab2_total, "Organised Results")

        self.layout.addWidget(self.tabs)

    def add_live_tab(self, name, confidence, image):
        new_data = self.LiveResultBlock(name, confidence, image, self.controller)
        list_item = QListWidgetItem()
        self.tab1_live.addItem(list_item)
        self.tab1_live.setItemWidget(list_item, new_data)
        list_item.setSizeHint(new_data.sizeHint())

    def get_live_list_widget(self):
        return self.tab1_live

    class LiveResultBlock(QWidget):
        WIDTH = 400
        HEIGHT = 120

        def __init__(self, name, confidence, image, controller):
            super(RightWidget.LiveResultBlock, self).__init__()
            self.controller = controller
            self.confidence = confidence
            self.name = name
            self.image_path = image
            self.__setup_block()

        def __setup_block(self):
            self.layout = QHBoxLayout()
            self.image_frame = QLabel(self)

            self.image_pixmap = QPixmap(self.image_path)

            self.image_frame.setPixmap(self.image_pixmap.scaled(self.WIDTH, self.HEIGHT, Qt.KeepAspectRatio))

            self.layout.addWidget(self.image_frame)

            self.__setup_data()
            self.__setup_buttons()

            self.setLayout(self.layout)

        def __setup_data(self):
            self.data_section = QWidget()
            self.data_section.setStyleSheet("border:1px solid rgb(0, 0, 0);")
            self.data_layout = QVBoxLayout()
            self.data_section.setLayout(self.data_layout)

            self.text_name = QLabel()
            self.text_name.setText("Name: " + self.name)
            text_confidence = QLabel()
            text_confidence.setText("Confidence: " + self.confidence)

            self.data_layout.addWidget(self.text_name)
            self.data_layout.addWidget(text_confidence)

            self.layout.addWidget(self.data_section)

        def __setup_buttons(self):
            self.button_section = QWidget()
            self.button_layout = QVBoxLayout()
            self.button_section.setLayout(self.button_layout)

            self.info_button = QPushButton(self.button_section)
            self.info_button.setText("INFO")

            self.modify_button = QPushButton(self.button_section)
            self.modify_button.setText("MODIFY")
            self.modify_button.clicked.connect(self.__modify_label)

            self.button_layout.addWidget(self.info_button)
            self.button_layout.addWidget(self.modify_button)

            self.layout.addWidget(self.button_section)

        def __modify_label(self):
            new_name, ok_pressed = QInputDialog.getText(self, "New Face Label","Name:", QLineEdit.Normal, self.name)

            if ok_pressed and new_name != self.name:
                self.text_name.setText("Name: " + new_name)
                self.controller.add_face_db(new_name, self.image_pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec()
