from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QComboBox, QCheckBox


class SettingsDialog(QDialog):
    def __init__(self, settings, controller):
        super(SettingsDialog, self).__init__()
        self.settings = settings
        self.controller = controller

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.select_accept)
        button_box.rejected.connect(self.select_reject)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._general_group_box())
        main_layout.addWidget(self._face_dec_group_box())
        main_layout.addWidget(self._super_res_group_box())
        main_layout.addWidget(self._face_reg_group_box())
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)
        self.setWindowTitle("Settings")

    def _general_group_box(self):
        """ Group box for general settings - Settings include: Preferred Hardware and Save Images toggle """
        general_group_box = QGroupBox("General")
        general_layout = QFormLayout()
        general_layout.addRow(QLabel("Preferred Hardware: "), self._show_hardware())
        general_layout.addRow(QLabel("Live Result Limit: "), self._max_faces())
        general_group_box.setLayout(general_layout)

        return general_group_box

    def _face_dec_group_box(self):
        """ Group box for Face Detection settings - Settings include: Detection Confidence and Video Capture/Writer
        FPS """
        face_dec_group_box = QGroupBox("Face Detection")
        face_dec_layout = QFormLayout()
        # TODO: Figure out how to detect valid sources
        face_dec_layout.addRow(QLabel("Webcam Source: "), QLabel("0"))
        face_dec_layout.addRow(QLabel("Webcam FPS (Limited by Hardware): "), self._webcam_fps())
        face_dec_layout.addRow(QLabel("Confidence: "), self._show_confidence())
        face_dec_layout.addRow(QLabel("Display Video Capture FPS: "), self._show_fps())
        face_dec_group_box.setLayout(face_dec_layout)

        return face_dec_group_box

    def _super_res_group_box(self):
        """ Group box for Super Resolution settings - Settings include: Toggle on/off """
        super_res_group_box = QGroupBox("Super Resolution")
        super_res_layout = QFormLayout()
        super_res_layout.addRow(QLabel("Use on low resolution images: "), self._toggle_sr())
        super_res_layout.addRow(QLabel("Upscale Factor: "), QLabel("4x"))
        super_res_group_box.setLayout(super_res_layout)

        return super_res_group_box

    def _face_reg_group_box(self):
        """ Group box for Face Recognition settings - Settings include: Minimum Confidence"""
        face_reg_group_box = QGroupBox("Face Recognition")
        face_reg_layout = QFormLayout()
        face_reg_layout.addRow(QLabel("Minimum Confidence: "), self._show_min_confidence())
        face_reg_group_box.setLayout(face_reg_layout)

        return face_reg_group_box

    def _show_hardware(self):
        self._hardware_combo_box = QComboBox()
        self._hardware_combo_box.addItem("GPU")
        self._hardware_combo_box.addItem("CPU")

        # Pull from settings
        setting_index = self.settings.value("Hardware", 0, int)
        self._hardware_combo_box.setCurrentIndex(setting_index)
        return self._hardware_combo_box

    def _max_faces(self):
        self._max_faces_combo_box = QComboBox()
        self._max_faces_combo_box.addItem("10")
        self._max_faces_combo_box.addItem("50")
        self._max_faces_combo_box.addItem("100")
        self._max_faces_combo_box.addItem("200")
        self._max_faces_combo_box.addItem("500")

        # Pull from settings
        setting_index = self.settings.value("Max Faces", "100", str)
        text_index = self._max_faces_combo_box.findText(setting_index)
        self._max_faces_combo_box.setCurrentIndex(text_index)
        return self._max_faces_combo_box

    def _webcam_fps(self):
        # Could do a slider
        self._webcam_fps_combo_box = QComboBox()
        self._webcam_fps_combo_box.addItem("1")
        self._webcam_fps_combo_box.addItem("15")
        self._webcam_fps_combo_box.addItem("30")
        self._webcam_fps_combo_box.addItem("60")

        # Pull from settings
        setting_index = self.settings.value("Webcam FPS", "15", str)
        text_index = self._webcam_fps_combo_box.findText(setting_index)
        self._webcam_fps_combo_box.setCurrentIndex(text_index)
        return self._webcam_fps_combo_box

    def _show_confidence(self):
        # Could do a slider
        self._confidence_combo_box = QComboBox()
        self._confidence_combo_box.addItem("0.2")
        self._confidence_combo_box.addItem("0.4")
        self._confidence_combo_box.addItem("0.6")
        self._confidence_combo_box.addItem("0.8")

        # Pull from settings
        setting_index = self.settings.value("Face Detection Confidence", "0.4", str)
        text_index = self._confidence_combo_box.findText(setting_index)
        self._confidence_combo_box.setCurrentIndex(text_index)
        return self._confidence_combo_box

    def _show_fps(self):
        # Limited based in original video fps
        self._fps_combo_box = QComboBox()
        self._fps_combo_box.addItem("1")

        # Pull from settings
        setting_index = self.settings.value("Video Capture FPS", "1", str)
        text_index = self._fps_combo_box.findText(setting_index)
        self._fps_combo_box.setCurrentIndex(text_index)
        return self._fps_combo_box

    def _toggle_sr(self):
        self._toggle_sr_check = QCheckBox()

        # Pull from settings
        setting_toggle = self.settings.value("Toggle SR", 0, int)
        self._toggle_sr_check.setCheckState(setting_toggle)
        return self._toggle_sr_check

    def _show_min_confidence(self):
        self._min_combo_box = QComboBox()
        self._min_combo_box.addItem("50")
        self._min_combo_box.addItem("60")
        self._min_combo_box.addItem("70")
        self._min_combo_box.addItem("80")
        self._min_combo_box.addItem("90")
        self._min_combo_box.addItem("100")

        # Pull from settings
        setting_index = self.settings.value("Face Recognition Minimum Confidence", "70", str)
        text_index = self._min_combo_box.findText(setting_index)
        self._min_combo_box.setCurrentIndex(text_index)
        return self._min_combo_box

    def select_accept(self):
        # Saves to settings
        self.settings.setValue("Hardware", self._hardware_combo_box.currentIndex())
        self.settings.setValue("Max Faces", self._max_faces_combo_box.currentText())
        self.settings.setValue("Webcam FPS", self._webcam_fps_combo_box.currentText())
        self.settings.setValue("Face Detection Confidence", self._confidence_combo_box.currentText())
        self.settings.setValue("Video Capture FPS", self._fps_combo_box.currentText())
        self.settings.setValue("Toggle SR", self._toggle_sr_check.checkState())
        self.settings.setValue("Face Recognition Minimum Confidence", self._min_combo_box.currentText())
        self.controller.get_logger_gui().info("Settings Accepted")
        self.accept()

    def select_reject(self):
        # Resets based on current settings
        self._hardware_combo_box.setCurrentIndex(self.settings.value("Hardware", 0, int))

        setting_value = self.settings.value("Max Faces", "100", str)
        self._max_faces_combo_box.setCurrentIndex(self._max_faces_combo_box.findText(setting_value))

        setting_value = self.settings.value("Webcam FPS", "15", str)
        self._webcam_fps_combo_box.setCurrentIndex(self._webcam_fps_combo_box.findText(setting_value))

        setting_value = self.settings.value("Face Detection Confidence", "0.4", str)
        self._confidence_combo_box.setCurrentIndex(self._confidence_combo_box.findText(setting_value))

        setting_value = self.settings.value("Video Capture FPS", "1", str)
        self._fps_combo_box.setCurrentIndex(self._fps_combo_box.findText(setting_value))

        self._toggle_sr_check.setCheckState(self.settings.value("Toggle SR", 0, int))

        setting_value = self.settings.value("Face Recognition Minimum Confidence", "70", str)
        self._min_combo_box.setCurrentIndex(self._min_combo_box.findText(setting_value))

        self.controller.get_logger_gui().info("Settings Rejected")
        self.reject()
