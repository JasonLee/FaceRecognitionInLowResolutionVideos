from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from facialDetection.facialDetectionManager import set_detection_confidence
import system
import sys
import torch


class Settings_page(QDialog):
    """This class defines setting page.
    Settings include: hardware setting, enable super resolution or not, scale factor setting for super resolution.
    
    Attributes:
        srToggleflag (bool): if super resolution model is enabled or not.
        saveImagesToggleflag (bool): if saving images is enabled or not.
    """
    def __init__(self, mainInterface):
        super(Settings_page, self).__init__()
        self.srToggleflag = True
        self.saveImagesToggleflag = True
        self.mainInterface = mainInterface
        self.__createFormGroupBox()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.__submit_close)
        buttonBox.rejected.connect(self.__reject_close)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.__generalGroupBox)
        mainLayout.addWidget(self.__detectionGroupBox)
        mainLayout.addWidget(self.__SRGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Settings")

    def __createFormGroupBox(self):
        self.__generalGroupBox = QGroupBox("General")
        layout = QFormLayout()
        layout.addRow(QLabel("Hardware:"), self.__setHardware())
        layout.addRow(QLabel("Save Images to folder:"), self.__toggleSaveImage())
        self.__generalGroupBox.setLayout(layout)

        self.__detectionGroupBox = QGroupBox("Face Detection")
        layout = QFormLayout()
        layout.addRow(QLabel("Detection Confidence:"), self.__setDetectionConfidence())
        self.__detectionGroupBox.setLayout(layout)

        self.__SRGroupBox = QGroupBox("Super Resolution")
        layout = QFormLayout()
        layout.addRow(QLabel("Super Resolution:"), self.__toggleSR())
        layout.addRow(QLabel("Upscale Factor:"), self.__setUpscaleFactor())

        self.__SRGroupBox.setLayout(layout)


    def __toggleSaveImage(self):
        self.__toggleSaveImageBox = QCheckBox()
        self.__toggleSaveImageBox.setCheckState(Qt.Checked)
        return self.__toggleSaveImageBox

    def __toggleSR(self):
        self.__toggleSRBox = QCheckBox()
        self.__toggleSRBox.setCheckState(Qt.Checked)
        return self.__toggleSRBox

    def __setUpscaleFactor(self):
        ufComboBox = QComboBox()
        # ufComboBox.addItem("x2")
        ufComboBox.addItem("x4")
        # ufComboBox.addItem("x8")
        ufComboBox.setCurrentIndex(0)
        ufComboBox.activated[str].connect(self.mainInterface.set_hardware)
        return ufComboBox

    def __setDetectionConfidence(self):
        ufComboBox = QComboBox()
        ufComboBox.addItem("0.2")
        ufComboBox.addItem("0.4")
        ufComboBox.addItem("0.6")
        ufComboBox.addItem("0.8")
        ufComboBox.setCurrentIndex(0)
        ufComboBox.activated[str].connect(set_detection_confidence)
        return ufComboBox

    def __setHardware(self):
        hardwareComboBox = QComboBox()
        hardwareComboBox.addItem("GPU")
        hardwareComboBox.addItem("CPU")
        if not torch.cuda.is_available():
            hardwareComboBox.setCurrentIndex(1)
            hardwareComboBox.setEnabled(False)
        hardwareComboBox.activated[str].connect(self.mainInterface.set_hardware)
        return hardwareComboBox

    def __submit_close(self):
        self.srToggleflag = self.__toggleSRBox.isChecked()
        self.saveImagesToggleflag = self.__toggleSaveImageBox.isChecked()
        print("ACCEPT CLOSE")
        self.accept()


    def __reject_close(self):
        print("REJECT CLOSE")
        self.reject()





