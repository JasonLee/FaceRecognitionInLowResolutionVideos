# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '01_RetinaGUI.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(887, 594)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.importButton = QtWidgets.QPushButton(self.centralwidget)
        self.importButton.setGeometry(QtCore.QRect(0, 0, 150, 60))

        font = QtGui.QFont()
        font.setPointSize(14)

        self.importButton.setFont(font)
        self.importButton.setIconSize(QtCore.QSize(16, 25))
        self.importButton.setObjectName("importButton")

        self.analysisButton = QtWidgets.QPushButton(self.centralwidget)
        self.analysisButton.setGeometry(QtCore.QRect(0, 50, 150, 60))

        font = QtGui.QFont()
        font.setPointSize(14)

        self.analysisButton.setFont(font)
        self.analysisButton.setObjectName("analysisButton")

        self.folderButton = QtWidgets.QPushButton(self.centralwidget)
        self.folderButton.setGeometry(QtCore.QRect(0, 100, 151, 61))

        font = QtGui.QFont()
        font.setPointSize(14)

        self.folderButton.setFont(font)
        self.folderButton.setObjectName("folderButton")

        self.helpButton = QtWidgets.QPushButton(self.centralwidget)
        self.helpButton.setGeometry(QtCore.QRect(0, 150, 150, 60))

        font = QtGui.QFont()
        font.setPointSize(14)

        self.helpButton.setFont(font)
        self.helpButton.setObjectName("helpButton")

        self.facesRecognised_label = QtWidgets.QLabel(self.centralwidget)
        self.facesRecognised_label.setGeometry(QtCore.QRect(600, 30, 181, 71))

        font = QtGui.QFont()
        font.setPointSize(18)

        self.facesRecognised_label.setFont(font)
        self.facesRecognised_label.setObjectName("facesRecognised_label")

        self.detectButton = QtWidgets.QPushButton(self.centralwidget)
        self.detectButton.setGeometry(QtCore.QRect(280, 350, 111, 31))
        self.detectButton.setObjectName("detectButton")

        self.facesDetected_label = QtWidgets.QLabel(self.centralwidget)
        self.facesDetected_label.setGeometry(QtCore.QRect(260, 30, 161, 71))

        font = QtGui.QFont()
        font.setPointSize(18)

        self.facesDetected_label.setFont(font)
        self.facesDetected_label.setObjectName("facesDetected_label")

        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider.setGeometry(QtCore.QRect(580, 390, 201, 51))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")

        self.database_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.database_lineEdit.setGeometry(QtCore.QRect(530, 310, 311, 31))
        self.database_lineEdit.setText("")
        self.database_lineEdit.setObjectName("database_lineEdit")

        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(340, 460, 241, 41))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")

        self.facesRecognised_label_2 = QtWidgets.QLabel(self.centralwidget)
        self.facesRecognised_label_2.setGeometry(QtCore.QRect(620, 360, 151, 31))

        font = QtGui.QFont()
        font.setPointSize(18)

        self.facesRecognised_label_2.setFont(font)
        self.facesRecognised_label_2.setObjectName("facesRecognised_label_2")

        self.barValue_label = QtWidgets.QLabel(self.centralwidget)
        self.barValue_label.setGeometry(QtCore.QRect(590, 470, 41, 16))

        font = QtGui.QFont()
        font.setPointSize(18)

        self.barValue_label.setFont(font)
        self.barValue_label.setObjectName("barValue_label")

        self.displayImage_label = QtWidgets.QLabel(self.centralwidget)
        self.displayImage_label.setGeometry(QtCore.QRect(180, 90, 311, 221))
        self.displayImage_label.setObjectName("displayImage_label")
        self.displayImage_label2 = QtWidgets.QLabel(self.centralwidget)
        self.displayImage_label2.setGeometry(QtCore.QRect(530, 90, 311, 221))
        self.displayImage_label2.setObjectName("displayImage_label2")

        self.percent_label = QtWidgets.QLabel(self.centralwidget)
        self.percent_label.setGeometry(QtCore.QRect(610, 470, 21, 16))

        font = QtGui.QFont()
        font.setPointSize(18)

        self.percent_label.setFont(font)
        self.percent_label.setObjectName("percent_label")

        self.facesRecognised_ValueLabel = QtWidgets.QLabel(self.centralwidget)
        self.facesRecognised_ValueLabel.setGeometry(QtCore.QRect(600, 366, 20, 20))

        font = QtGui.QFont()
        font.setPointSize(18)

        self.facesRecognised_ValueLabel.setFont(font)
        self.facesRecognised_ValueLabel.setObjectName("facesRecognised_ValueLabel")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 887, 22))
        self.menubar.setObjectName("menubar")

        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")

        self.menuFile_2 = QtWidgets.QMenu(self.menubar)
        self.menuFile_2.setObjectName("menuFile_2")

        self.menuSave_Preferences = QtWidgets.QMenu(self.menuFile_2)
        self.menuSave_Preferences.setObjectName("menuSave_Preferences")

        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")

        MainWindow.setStatusBar(self.statusbar)
        self.actionAbout_Retina = QtWidgets.QAction(MainWindow)
        self.actionAbout_Retina.setObjectName("actionAbout_Retina")

        self.actionQuit_Retina = QtWidgets.QAction(MainWindow)
        self.actionQuit_Retina.setObjectName("actionQuit_Retina")

        self.actionPreferences = QtWidgets.QAction(MainWindow)
        self.actionPreferences.setObjectName("actionPreferences")

        self.actionEnable_auto_save = QtWidgets.QAction(MainWindow)
        self.actionEnable_auto_save.setObjectName("actionEnable_auto_save")

        self.actionDisable_auto_save = QtWidgets.QAction(MainWindow)
        self.actionDisable_auto_save.setObjectName("actionDisable_auto_save")

        self.actionImport_Image = QtWidgets.QAction(MainWindow)
        self.actionImport_Image.setObjectName("actionImport_Image")

        self.menuFile.addAction(self.actionAbout_Retina)
        self.menuFile.addAction(self.actionQuit_Retina)

        self.menuSave_Preferences.addAction(self.actionEnable_auto_save)
        self.menuSave_Preferences.addAction(self.actionDisable_auto_save)

        self.menuFile_2.addAction(self.actionImport_Image)
        self.menuFile_2.addAction(self.menuSave_Preferences.menuAction())

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuFile_2.menuAction())

        self.retranslateUi(MainWindow)
        self.detectButton.clicked.connect(self.displayImage_label.update)
        self.progressBar.valueChanged['int'].connect(self.barValue_label.setNum)
        self.horizontalSlider.sliderMoved['int'].connect(self.displayImage_label2.update)
        self.importButton.clicked.connect(MainWindow.importImage)
        self.actionQuit_Retina.triggered.connect(MainWindow.close)
        self.actionAbout_Retina.triggered.connect(MainWindow.aboutWindow)
        self.actionImport_Image.triggered.connect(MainWindow.importImage)
        self.actionEnable_auto_save.triggered.connect(MainWindow.enableAutosave)
        self.actionDisable_auto_save.triggered.connect(MainWindow.disableAutosave)
        self.analysisButton.clicked.connect(MainWindow.showAnalysis)
        self.folderButton.clicked.connect(MainWindow.showFolders)
        self.helpButton.clicked.connect(MainWindow.showHelp)
        self.database_lineEdit.returnPressed.connect(MainWindow.updateDatabase)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

        self.importButton.setText(_translate("MainWindow", "Import Image"))
        self.analysisButton.setText(_translate("MainWindow", "Analysis"))
        self.folderButton.setText(_translate("MainWindow", "Folders"))
        self.helpButton.setText(_translate("MainWindow", "Help"))
        self.facesRecognised_label.setText(_translate("MainWindow", "FACES RECOGNISED"))
        self.detectButton.setText(_translate("MainWindow", "DETECT"))
        self.facesDetected_label.setText(_translate("MainWindow", "FACES DETECTED"))
        self.facesRecognised_label_2.setText(_translate("MainWindow", "faces recognised"))
        self.barValue_label.setText(_translate("MainWindow", "0"))
        self.displayImage_label.setText(_translate("MainWindow", "Display Image"))
        self.displayImage_label2.setText(_translate("MainWindow", "Display Image"))
        self.percent_label.setText(_translate("MainWindow", "%"))
        self.facesRecognised_ValueLabel.setText(_translate("MainWindow", "0"))
        self.menuFile.setTitle(_translate("MainWindow", "Retina"))
        self.menuFile_2.setTitle(_translate("MainWindow", "File"))
        self.menuSave_Preferences.setTitle(_translate("MainWindow", "Save Preferences"))
        self.actionAbout_Retina.setText(_translate("MainWindow", "About Retina"))
        self.actionQuit_Retina.setText(_translate("MainWindow", "Quit Retina"))
        self.actionPreferences.setText(_translate("MainWindow", "Preferences"))
        self.actionEnable_auto_save.setText(_translate("MainWindow", "Enable auto-save"))
        self.actionDisable_auto_save.setText(_translate("MainWindow", "Disable auto-save"))
        self.actionImport_Image.setText(_translate("MainWindow", "Import Image"))


