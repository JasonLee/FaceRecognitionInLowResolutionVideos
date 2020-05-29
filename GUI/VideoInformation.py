from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGroupBox, QFormLayout, QLabel
# Importing just for values for "get" function of video stream without hard coding it
import cv2
import datetime as dt


class VideoInformationDialog(QDialog):
    def __init__(self, controller, parent):
        super(VideoInformationDialog, self).__init__()
        self.controller = controller
        self.parent = parent
        self.video_info_cv2 = None

        self._video_title = QLabel()
        self._video_length = QLabel()
        self._video_format = QLabel()
        self._video_dimensions = QLabel()
        self._fps = QLabel()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._general_group_box())

        self.setLayout(main_layout)
        self.setWindowTitle("Video Information")

    def open(self):
        self.video_info_cv2 = self.controller.get_current_video_cv2()

        if self.controller.get_current_video_cv2() is None:
            self.controller.get_logger_gui().error("Error: Video has not loaded. No information can be retrieved")
            return

        self.setup_info()

    def _general_group_box(self):
        """ Group box video information """
        general_group_box = QGroupBox("Video Information")
        general_layout = QFormLayout()
        general_layout.addRow(QLabel("File Path: "),  self._video_title)
        general_layout.addRow(QLabel("Format: "), self._video_format)
        general_layout.addRow(QLabel("Dimensions: "), self._video_dimensions)
        general_layout.addRow(QLabel("Length: "), self._video_length)
        general_layout.addRow(QLabel("FPS: "), self._fps)
        general_group_box.setLayout(general_layout)

        return general_group_box

    def setup_info(self):
        cv2_video = self.controller.get_current_video_cv2()
        cv2_video.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)

        width = int(cv2_video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cv2_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cv2_video.get(cv2.CAP_PROP_FPS))

        video_length_seconds = cv2_video.get(cv2.CAP_PROP_FRAME_COUNT) / fps
        processed_time = dt.timedelta(seconds=video_length_seconds)
        # Toss milliseconds, internally milliseconds are converted to microseconds
        processed_time = str(processed_time - dt.timedelta(microseconds=processed_time.microseconds))

        self._video_title.setText(self.parent.video_path)
        self._video_length.setText(str(processed_time))
        self._video_format.setText("mp4")
        self._video_dimensions.setText(str(height) + 'x' + str(width))
        self._fps.setText(str(fps))

