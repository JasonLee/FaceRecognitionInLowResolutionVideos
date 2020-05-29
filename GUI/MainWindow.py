import logging
import os
import shutil
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QHBoxLayout,
                             QLabel, QMainWindow, QMenuBar,
                             QSplitter, QWidget, QStackedWidget, QMessageBox)

from GUI.GraphWidget import GraphWidget
from GUI.ListWidget import ListWidget
from GUI.VideoPlayer import VideoPlayer
from GUI.Settings import SettingsDialog

INPATH = 'input'
OUTPATH = 'out'
SELFPATH = '../userInteface'
LOG_PATH = 'logging'

IMAGE_VIEW = 0
VIDEO_VIEW = 1

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

        self.__list_widget = ListWidget(controller)
        self.__settings_page = SettingsDialog(self.controller.get_settings(), controller)
        self.__settings_page.hide()

        self.__setup_menu_bar()
        self.__setup_toolbar()
        self.__setup_layout()

        self.is_webcam_active = False
        self.is_processing_video = False

    def __setup_menu_bar(self):
        self.menu_bar = QMenuBar()

        def action_mapper(action_name, function_to_connect):
            new_action = QAction(action_name, self)
            new_action.triggered.connect(function_to_connect)
            return new_action

        self.file_menu = self.menu_bar.addMenu('File')
        self.menu_bar.addAction(action_mapper('Settings', self.__open_settings))
        self.menu_bar.addAction(action_mapper('Exit', self.close))

        self.file_menu.addAction(action_mapper('print', self.print_test))
        self.file_menu.addAction(action_mapper('Import Images', self.__import_image_func))
        self.file_menu.addAction(action_mapper('Import Videos', self.__import_video_func))
        self.file_menu.addAction(action_mapper('Use Webcam Feed', self.__use_webcam_func))

        self.setMenuBar(self.menu_bar)
        self.controller.get_logger_gui().info("Setup Menu Bar")

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
        # self.toolbar.addAction(self.tick_button)
        self.toolbar.addAction(self.cross_button)
        self.controller.get_logger_gui().info("Setup Tool Bar")

    def __setup_layout(self):
        layout = QHBoxLayout()

        self.image_video_view = QStackedWidget()

        self.image_frame_label = QLabel(self)

        self.video_display_widget = QStackedWidget()
        self.__video_player = VideoPlayer(self, self.controller)

        self.video_processing_label = QLabel(self)

        self.video_display_widget.addWidget(self.__video_player)
        self.video_display_widget.addWidget(self.video_processing_label)
        self.video_display_widget.setCurrentIndex(0)
        self.controller.get_logger_gui().info("Setup Video Player")

        self.image_video_view.addWidget(self.image_frame_label)
        self.image_video_view.addWidget(self.video_display_widget)

        # Graph placeholder
        self.__graph_widget = GraphWidget(self.controller)
        self.controller.get_logger_gui().info("Setup Graph Widget")

        self.splitter_h = QSplitter(Qt.Horizontal)
        self.splitter_h.setChildrenCollapsible(False)

        self.splitter_h.setSizes([600, 600])

        self.splitter_v = QSplitter(Qt.Vertical)
        self.splitter_v.setChildrenCollapsible(False)
        self.splitter_v.addWidget(self.splitter_h)
        self.splitter_v.addWidget(self.__graph_widget)
        self.splitter_v.setSizes([800, 400])

        layout.addWidget(self.splitter_v)

        self.main_widget.setLayout(layout)

        # Placed here due to an issue with setGeometry in Windows and QVideoWidget not liking it.
        self.splitter_h.addWidget(self.image_video_view)
        self.splitter_h.addWidget(self.__list_widget)

        # TEST BUTTON WIRE WITH FUNCTION AS NECESSARY
        self.test_action = QAction('TEST BUTTON', self)
        self.test_action.triggered.connect(self.get_graph_widget().plot)
        # self.menu_bar.addAction(self.test_action)
        self.controller.get_logger_gui().info("Setup Widgets")

    def __open_settings(self):
        self.__settings_page.open()
        result = self.__settings_page.exec()

        # Might not be needed
        if result:
            self.controller.get_logger_gui().info("Open Settings")
            reset_prompt = QMessageBox(QMessageBox.Information, "Settings", "Restart application to apply changes")
            reset_prompt.exec()

    def __import_image_func(self):
        self.controller.get_logger_gui().info("Clicked Import Image")
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File (*.jpg) (*.png)", "C:", "Images(*.jpg *.png)")

        if len(file_path) > 0:
            self.image_video_view.setCurrentIndex(IMAGE_VIEW)
            self.reset_folders_lists()
            shutil.copy(file_path, INPATH)

            file_name = os.path.basename(file_path)

            self.__start_detection(file_name)

    def __import_video_func(self):
        self.controller.get_logger_gui().info("Clicked Import Video")
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File (*.mp4)", "C:", "Video Files (*.mp4)")

        if len(file_path) > 0:
            self.image_video_view.setCurrentIndex(VIDEO_VIEW)
            self.reset_folders_lists()
            shutil.copy(file_path, INPATH)
            self.__video_player.set_video(file_path)

    def __use_webcam_func(self):
        self.controller.get_logger_gui().info("Clicked Use Webcam")
        self.image_video_view.setCurrentIndex(IMAGE_VIEW)
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
            self.controller.get_logger_gui().info("Cancel webcam")
            self.is_webcam_active = False
            self.cross_button.setDisabled(False)
        elif self.is_processing_video is True:
            self.controller.get_logger_gui().info("Cancel processing video")
            self.controller.empty_all_queues()
            self.cross_button.setDisabled(False)
            self.is_processing_video = False

    def is_webcam_activated(self):
        return self.is_webcam_active

    def reset_frame(self):
        self.cross_button.setDisabled(True)
        self.clear_image_frame()

    def __start_detection(self, file_name):
        file_name = os.path.join(INPATH, file_name)
        self.set_image_frame(file_name)

        # file_name doesn't actually do anything. Works by taking the image from /input
        self.controller.image_selected()

    def set_image_frame(self, image_name):
        w = self.image_frame_label.width()
        h = self.image_frame_label.height()

        pixmap = QPixmap(image_name)

        self.image_frame_label.setPixmap(pixmap.scaled(w, h, Qt.KeepAspectRatio))

    def set_video_processing_frame(self, image_name):
        w = self.video_processing_label.width()
        h = self.video_processing_label.height()

        pixmap = QPixmap(image_name)
        self.video_processing_label.setPixmap(pixmap.scaled(w, h, Qt.KeepAspectRatio))

    def clear_image_frame(self):
        self.image_frame_label.clear()

    def get_list_widget(self):
        return self.__list_widget

    def get_graph_widget(self):
        return self.__graph_widget

    def get_video_player(self):
        return self.__video_player

    def get_settings_page(self):
        return self.__settings_page

    def reset_folders_lists(self):
        self.controller.get_logger_gui().info("Reset folders and release video")
        self.__video_player.release_video()
        for f in os.listdir(INPATH):
            file_path = os.path.join(INPATH, f)
            os.unlink(file_path)
        for f in os.listdir(OUTPATH):
            file_path = os.path.join(OUTPATH, f)
            os.unlink(file_path)

        self.get_list_widget().get_live_list_widget().clear()

        self.get_graph_widget().reset_figure()

    def print_test(self):
        print("TEST")

    def get_status(self):
        # 0 is Image view / 1 is Video View
        return self.image_video_view.currentIndex()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec()
