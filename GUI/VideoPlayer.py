from PyQt5.QtCore import QSize, Qt, QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QWidget, QPushButton, QStyle, QSlider, QStatusBar, QHBoxLayout, QVBoxLayout, QLabel
from GUI.VideoInformation import VideoInformationDialog
import datetime as dt


class VideoPlayer(QWidget):
    def __init__(self, parent_container, controller):
        super(VideoPlayer, self).__init__()
        self.parent_container = parent_container
        self.controller = controller
        self.video_path = None

        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        self.video_widget = QVideoWidget(self)

        self.__set_buttons()

        self.video_info_dialog = VideoInformationDialog(self.controller, self)
        self.video_info_dialog.hide()

        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.stateChanged.connect(self.media_state_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.error.connect(self.handle_error)
        self.status_bar.showMessage("Ready")

    def __set_buttons(self):
        btn_size = QSize(16, 16)

        self.play_button = QPushButton()
        self.play_button.setFixedHeight(24)
        self.play_button.setIconSize(btn_size)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play)

        self.info_button = QPushButton()
        self.info_button.setFixedHeight(24)
        self.info_button.setIconSize(btn_size)
        self.info_button.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))
        self.info_button.clicked.connect(self.show_info)

        self.process_button = QPushButton()
        self.process_button.setText("Process")
        self.process_button.setFixedHeight(24)
        self.process_button.setIconSize(btn_size)
        self.process_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogInfoView))
        self.process_button.clicked.connect(self.process_video)

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)

        self.status_bar = QStatusBar()
        self.status_bar.setFont(QFont("Noto Sans", 7))
        self.status_bar.setFixedHeight(14)

        self.video_time_label = QLabel()
        self.video_time_label.setFixedHeight(16)

        self.position_slider.valueChanged.connect(self.set_video_label)

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.info_button)
        control_layout.addWidget(self.process_button)
        control_layout.addWidget(self.position_slider)
        control_layout.addWidget(self.video_time_label)

        layout = QVBoxLayout()

        layout.addWidget(self.video_widget)
        layout.addLayout(control_layout)
        layout.addWidget(self.status_bar)

        self.setLayout(layout)

    def set_video(self, file_path):
        """ Sets Video based on Video path. """
        self.video_path = file_path
        self.process_button.setDisabled(False)
        print(file_path)
        self.controller.get_logger_gui().info("Pull in new video path: " + self.video_path)
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
        self.status_bar.showMessage(file_path)
        self.play()

    def show_info(self):
        self.controller.set_current_video_cv2(self.video_path)
        self.video_info_dialog.open()
        self.video_info_dialog.exec()
        self.controller.set_current_video_cv2(None)

    def set_video_label(self, time):
        processed_time = dt.timedelta(milliseconds=time)
        # Toss milliseconds, internally milliseconds are converted to microseconds
        new_time = str(processed_time - dt.timedelta(microseconds=processed_time.microseconds))
        self.video_time_label.setText(new_time)

    def release_video(self):
        """ Used when resetting folders to give control of video back to OS"""
        self.media_player.setMedia(QMediaContent())

    def process_video(self):
        """ Starts detection process"""
        self.controller.get_logger_gui().info("Processing Video")
        self.controller.set_disabled_cross_button(False)
        self.parent_container.video_display_widget.setCurrentIndex(1)
        self.controller.image_selected()
        self.media_player.pause()
        self.process_button.setDisabled(True)

    def play(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def media_state_changed(self):
        """ Controls pause button """
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def position_changed(self, position):
        """ Signal when video updates"""
        self.position_slider.setValue(position)

    def duration_changed(self, duration):
        """ Updates on new video"""
        self.position_slider.setRange(0, duration)

    def set_position(self, position):
        """ Slider in player"""
        self.media_player.setPosition(position)

    def handle_error(self):
        self.play_button.setEnabled(False)
        self.status_bar.showMessage("Error: " + self.media_player.errorString())
        self.controller.get_logger_gui().error("Video Player Error: " + self.media_player.errorString())

