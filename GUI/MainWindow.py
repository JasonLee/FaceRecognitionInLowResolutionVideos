import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtWidgets import (QAction, QFileDialog, QHBoxLayout,
                             QLabel, QMainWindow, QMenuBar,
                             QSplitter, QWidget, QStackedWidget, QMessageBox)

from GUI.DBRemoveDialog import RemoveFaceDialog, RemovePeopleDialog
from GUI.DbAddDialog import AddingPeopleDialog, AddingFaceDialog
from GUI.GraphWidget import GraphWidget
from GUI.ListWidget import ListWidget
from GUI.Settings import SettingsDialog
from GUI.VideoPlayer import VideoPlayer
from database.database import get_all_people_names_unsafe

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

        self._list_widget = ListWidget(controller)
        self._settings_page = SettingsDialog(self.controller.get_settings(), controller)
        self._settings_page.hide()

        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_layout()

        self.is_webcam_active = False
        self.is_processing_video = False

    def _setup_menu_bar(self):
        self.menu_bar = QMenuBar()

        def action_mapper(action_name, function_to_connect):
            new_action = QAction(action_name, self)
            new_action.triggered.connect(function_to_connect)
            return new_action

        self.file_menu = self.menu_bar.addMenu('File')
        self.menu_bar.addAction(action_mapper('Settings', self._open_settings))
        self.menu_bar.addAction(action_mapper('Exit', self.close))

        self.file_menu.addAction(action_mapper('Import Images', self._import_image_func))
        self.file_menu.addAction(action_mapper('Import Videos', self._import_video_func))
        self.file_menu.addAction(action_mapper('Use Webcam Feed', self._use_webcam_func))

        self.setMenuBar(self.menu_bar)
        self.controller.get_logger_gui().info("Setup Menu Bar")

    def _setup_toolbar(self):
        self.toolbar = self.addToolBar("Main")

        # Nicer way of adding function action to buttons
        def icon_action_mapper(icon_path, action_name, function_to_connect, tooltip):
            new_action = QAction(QIcon(icon_path), action_name, self)
            new_action.triggered.connect(function_to_connect)
            new_action.setToolTip(tooltip)
            return new_action

        self.import_images_button = icon_action_mapper(
            ICON_IMAGE_PATH + "camera_icon.png", "new", self._import_image_func, "Import Images")

        self.import_videos_button = icon_action_mapper(
            ICON_IMAGE_PATH + "video_camera_icon.png", "new", self._import_video_func, "Import Videos")

        self.webcam_button = icon_action_mapper(
            ICON_IMAGE_PATH + "webcam_icon.png", "new", self._use_webcam_func, "Use Webcam feed")

        self.cross_button = icon_action_mapper(
            ICON_IMAGE_PATH + "cross_icon.png", "new", self._cross_func, "Cancel current event")
        self.cross_button.setDisabled(True)

        self.add_person_to_db = icon_action_mapper(
            ICON_IMAGE_PATH + "db_add.png", "new", self._db_add_person, "Add person to db")

        self.add_face_to_db = icon_action_mapper(
            ICON_IMAGE_PATH + "image_add.png", "new", self._db_add_face_image, "Add identifying face to db")

        self.remove_people_from_db = icon_action_mapper(
            ICON_IMAGE_PATH + "db_remove.png", "new", self._db_remove_people, "Remove person from db")

        self.remove_image_from_db = icon_action_mapper(
            ICON_IMAGE_PATH + "image_remove.png", "new", self._db_remove_face_image, "Remove face image from db")

        self.toolbar.addAction(self.import_images_button)
        self.toolbar.addAction(self.import_videos_button)
        self.toolbar.addAction(self.webcam_button)

        self.toolbar.addSeparator()
        self.toolbar.addAction(self.cross_button)
        self.toolbar.addSeparator()

        self.toolbar.addAction(self.add_person_to_db)
        self.toolbar.addAction(self.add_face_to_db)
        self.toolbar.addSeparator()

        self.toolbar.addAction(self.remove_people_from_db)
        self.toolbar.addAction(self.remove_image_from_db)

        self.controller.get_logger_gui().info("Setup Tool Bar")

    def _setup_layout(self):
        layout = QHBoxLayout()

        self.image_video_view = QStackedWidget()

        self.image_frame_label = QLabel(self)

        self.video_display_widget = QStackedWidget()
        self._video_player = VideoPlayer(self, self.controller)

        self.video_processing_label = QLabel(self)

        self.video_display_widget.addWidget(self._video_player)
        self.video_display_widget.addWidget(self.video_processing_label)
        self.video_display_widget.setCurrentIndex(0)
        self.controller.get_logger_gui().info("Setup Video Player")

        self.image_video_view.addWidget(self.image_frame_label)
        self.image_video_view.addWidget(self.video_display_widget)

        # Graph placeholder
        self._graph_widget = GraphWidget(self.controller)
        self.controller.get_logger_gui().info("Setup Graph Widget")

        self.splitter_h = QSplitter(Qt.Horizontal)
        self.splitter_h.setChildrenCollapsible(False)

        self.splitter_h.setSizes([600, 600])

        self.splitter_v = QSplitter(Qt.Vertical)
        self.splitter_v.setChildrenCollapsible(False)
        self.splitter_v.addWidget(self.splitter_h)
        self.splitter_v.addWidget(self._graph_widget)
        self.splitter_v.setSizes([800, 400])

        layout.addWidget(self.splitter_v)

        self.main_widget.setLayout(layout)

        # Placed here due to an issue with setGeometry in Windows and QVideoWidget not liking it.
        self.splitter_h.addWidget(self.image_video_view)
        self.splitter_h.addWidget(self._list_widget)

        # TEST BUTTON WIRE WITH FUNCTION AS NECESSARY
        self.test_action = QAction('TEST BUTTON', self)
        self.test_action.triggered.connect(self.get_graph_widget().plot)
        # self.menu_bar.addAction(self.test_action)
        self.controller.get_logger_gui().info("Setup Widgets")

    def _open_settings(self):
        self._settings_page.open()
        result = self._settings_page.exec()

        # Might not be needed
        if result:
            self.controller.get_logger_gui().info("Open Settings")
            reset_prompt = QMessageBox(QMessageBox.Information, "Settings", "Restart application to apply changes")
            reset_prompt.exec()

    def _import_image_func(self):
        self.controller.get_logger_gui().info("Clicked Import Image")
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File (*.jpg) (*.png)", "C:", "Images(*.jpg *.png)")

        if len(file_path) > 0:
            self.image_video_view.setCurrentIndex(IMAGE_VIEW)
            self.reset_folders_lists()

            self.controller.set_file_path(file_path)

            self._setup_view_image(file_path)

    def _import_video_func(self):
        self.controller.get_logger_gui().info("Clicked Import Video")
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File (*.mp4)", "C:", "Video Files (*.mp4)")

        if len(file_path) > 0:
            self.image_video_view.setCurrentIndex(VIDEO_VIEW)
            self.reset_folders_lists()

            self.controller.set_file_path(file_path)
            self._video_player.set_video(file_path)

    def _use_webcam_func(self):
        self.controller.get_logger_gui().info("Clicked Use Webcam")
        self.image_video_view.setCurrentIndex(IMAGE_VIEW)
        self.cross_button.setDisabled(False)
        self.is_webcam_active = True
        self.reset_folders_lists()
        self.controller.webcam_activated()

    # Do as required
    def _cross_func(self):
        if self.is_webcam_active is True:
            self.controller.get_logger_gui().info("Cancel webcam")
            self.is_webcam_active = False
            self.cross_button.setDisabled(False)
        elif self.is_processing_video is True:
            self.controller.get_logger_gui().info("Cancel processing video")
            self.cross_button.setDisabled(False)
            self.is_processing_video = False

    def _db_add_person(self):
        add_people_page = AddingPeopleDialog(self.controller)
        add_people_page.open()
        add_people_page.exec()
        del add_people_page

    def _db_add_face_image(self):
        if self._does_db_contain_people():
            add_face_page = AddingFaceDialog(self.controller)
            add_face_page.open()
            add_face_page.exec()
            del add_face_page

    def _db_remove_people(self):
        if self._does_db_contain_people():
            remove_people_page = RemovePeopleDialog(self.controller)
            remove_people_page.open()
            remove_people_page.exec()
            del remove_people_page

    def _db_remove_face_image(self):
        if self._does_db_contain_people():
            remove_face_page = RemoveFaceDialog(self.controller)
            remove_face_page.open()
            remove_face_page.exec()
            del remove_face_page

    def _does_db_contain_people(self):
        if len(get_all_people_names_unsafe()) == 0:
            reset_prompt = QMessageBox(QMessageBox.Information, "Warning", "Please add a person first.")
            reset_prompt.exec()
            return False
        else:
            return True

    def is_webcam_activated(self):
        return self.is_webcam_active

    def reset_frame(self):
        self.cross_button.setDisabled(True)
        self.clear_image_frame()

    def _setup_view_image(self, file_name):
        self.set_image_frame(file_name)

        # file_name doesn't actually do anything. Works by taking the image from /input
        self.controller.image_selected()

    def cv2_to_QImage(self, image_numpy_arr):
        # Convert to QImage for GUI
        height, width, channel = image_numpy_arr.shape
        bytesPerLine = 3 * width

        return QImage(image_numpy_arr.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

    def set_image_frame(self, image):
        w = self.image_frame_label.width()
        h = self.image_frame_label.height()

        # Image is path when image is imported from dir
        if isinstance(image, str):
            pixmap = QPixmap(image)
        else:
            pixmap = QPixmap(self.cv2_to_QImage(image))

        self.image_frame_label.setPixmap(pixmap.scaled(w, h, Qt.KeepAspectRatio))

    def set_video_processing_frame(self, image):
        w = self.video_processing_label.width()
        h = self.video_processing_label.height()

        pixmap = QPixmap(self.cv2_to_QImage(image))

        self.video_processing_label.setPixmap(pixmap.scaled(w, h, Qt.KeepAspectRatio))

    def clear_image_frame(self):
        self.image_frame_label.clear()

    def get_list_widget(self):
        return self._list_widget

    def get_graph_widget(self):
        return self._graph_widget

    def get_video_player(self):
        return self._video_player

    def get_settings_page(self):
        return self._settings_page

    def reset_folders_lists(self):
        self.controller.get_logger_gui().info("Reset folders and release video")
        self._video_player.release_video()
        for f in os.listdir(OUTPATH):
            file_path = os.path.join(OUTPATH, f)
            os.unlink(file_path)

        self.get_list_widget().get_live_list_widget().clear()
        self.get_list_widget().get_total_list_widget().clear()
        self.get_list_widget().reset_total_list_dict()

        self.get_graph_widget().reset_figure()

    def get_status(self):
        """ What is currently being displayed """
        # 0 is Image view / 1 is Video View
        return self.image_video_view.currentIndex()
