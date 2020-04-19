from PyQt5 import QtCore, QtGui, QtWidgets
from userInteface.about_page import *
from userInteface.settings_page import *
import shutil, os, threading, numpy
from superResolution.Srgan_Utils import *
from FaceRec.Rec_Utils import *

INPATH = './input'
OUTPATH = './out'
SELFPATH = './userInteface'


class Ui_MainWindow(object):
    """The class defines main GUI window to show.

    Attributes:
        __about_page: a window containing information about the system (QMainWindow)
        __settings_page: a window containing settings for the system (QMainWindow)
    """
    def __init__(self):
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
        self.hardware = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.__about_page = About_page()
        self.__settings_page = Settings_page(self)
        self.srganModel = superResolutionModel(self.hardware)
        self.recogModel = recognitionModel("./images", self.hardware)
        self.forImage = True
    def setupUi(self, MainWindow, startMethod):
        """Sets up the GUI

        Args:
            MainWindow: main window to display GUI.
            startMethod: method to choose model and start processing video/image.
        """
        self.mainWindow = MainWindow
        self.mainWindow.setObjectName("MainWindow")
        self.mainWindow.resize(890, 590)
        self.startMethod = startMethod
        self.__setupCentralWidget()
        self.__setupButtons()
        self.__setupLabels()
        self.__setupDatabaseInput()
        self.__setupStatusBar()
        self.__setupMenubarAndMenus()
        self.__initActions()
        self.__mapActionsToObjects()
        self.__retranslateUi()
        self.__faceGallery = []
        self.__faceList = []
        self.__faceSelected = 0
        self.__detGallery = []
        self.__detSelected = 0
        self.stopRecording = False

    def __setupCentralWidget(self):
        """configures and attaches central widget to the main window"""
        self.centralwidget = QtWidgets.QWidget(self.mainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.mainWindow.setCentralWidget(self.centralwidget)

    def __setupButtons(self):
        """configures and attaches all buttons to the central widget"""

        def makeButton(fontsize, geometry, name):
            """designs and attaches a button to the central widget"""
            font = QtGui.QFont()
            font.setPointSize(fontsize)
            button = QtWidgets.QPushButton(self.centralwidget)
            button.setGeometry(geometry)
            button.setFont(font)
            button.setObjectName(name)
            return button

        self.importButton = makeButton(14, QtCore.QRect(5, 5, 155, 60), "importButton")
        self.clearButton = makeButton(14, QtCore.QRect(5, 70, 155, 60), "clearButton")
        self.webcamButton = makeButton(14, QtCore.QRect(5, 135, 155, 60), "webcamButton")
        self.stopButton = makeButton(14, QtCore.QRect(5, 135, 155, 60), "stopButton")
        self.stopButton.hide()
        self.refreshButton = makeButton(14, QtCore.QRect(5, 200, 155, 60), "refreshButton")
        self.nextRecognisedButton = makeButton(14, QtCore.QRect(540, 435, 160, 30), "nextRecognisedButton")
        self.prevRecognisedButton = makeButton(14, QtCore.QRect(710, 435, 160, 30), "prevRecognisedButton")
        self.nextRecognisedButton.setDisabled(True)
        self.prevRecognisedButton.setDisabled(True)
        self.nextDetectedButton = makeButton(14, QtCore.QRect(180, 435, 160, 30), "nextDetectedButton")
        self.prevDetectedButton = makeButton(14, QtCore.QRect(350, 435, 160, 30), "prevDetectedButton")
        self.nextDetectedButton.setDisabled(True)
        self.prevDetectedButton.setDisabled(True)

    def __setupLabels(self):
        """configures and attaches all labels to the central widget"""

        def makeLabel(fontsize, geometry, name):
            """designs and attaches a label to the central widget"""
            font = QtGui.QFont()
            font.setPointSize(fontsize)
            label = QtWidgets.QLabel(self.centralwidget)
            label.setGeometry(geometry)
            label.setFont(font)
            label.setObjectName(name)
            return label

        self.facesRecLabel = makeLabel(18, QtCore.QRect(595, 10, 220, 20), "facesRecLabel")
        self.facesRecLabel2 = makeLabel(14, QtCore.QRect(610, 470, 160, 25), "facesRecLabel2")
        self.currentFace = makeLabel(14, QtCore.QRect(730, 470, 160, 25), "currentFace")
        self.confidenceLabel = makeLabel(16, QtCore.QRect(720, 502.5, 50, 25), "confidenceLabel")
        self.accuracyLabel = makeLabel(14, QtCore.QRect(610, 500, 350, 30), "accuracyLabel")
        self.loadedLabel = makeLabel(14, QtCore.QRect(180, 500, 330, 25), "loadedLabel")
        self.framelabel = makeLabel(14, QtCore.QRect(180, 470, 330, 25), "framelabel")
        

        self.dispImageLabel = QtWidgets.QLabel(self.centralwidget)
        self.dispImageLabel.setGeometry(QtCore.QRect(170, 40, 350, 350))
        self.dispImageLabel2 = QtWidgets.QLabel(self.centralwidget)
        self.dispImageLabel2.setGeometry(QtCore.QRect(530, 40, 350, 350))

        pixmap = QtGui.QPixmap(SELFPATH + '/retinaLogo.png')
        self.logoImageLabel = QtWidgets.QLabel(self.centralwidget)
        self.logoImageLabel.setPixmap(pixmap)
        self.logoImageLabel.setGeometry(QtCore.QRect(5, 270, 155, 290))
        self.logoImageLabel.show()



    def __setupDatabaseInput(self):
        """Configures the database input bar (used to manually identify faces) and attaches it to the central widget"""
        self.databaseInput = QtWidgets.QLineEdit(self.centralwidget)
        self.databaseInput.setGeometry(QtCore.QRect(540, 400, 330, 30))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.databaseInput.setFont(font)
        self.databaseInput.setText("")
        self.databaseInput.setObjectName("databaseInput")
        self.databaseInput.setReadOnly(True)
    def __setupStatusBar(self):
        """Configures the status bar and attaches it to the main window"""
        self.statusbar = QtWidgets.QStatusBar(self.centralwidget)
        self.statusbar.setObjectName("statusbar")

    def __setupMenubarAndMenus(self):
        """configures the menu bar and attaches it to the main window"""

        def makeMenu(attachpoint,name):
            """initialises a menu and attaches it to the menu bar"""
            menu = QtWidgets.QMenu(attachpoint)
            menu.setObjectName(name)
            return menu

        self.menubar = QtWidgets.QMenuBar(self.mainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 887, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = makeMenu(self.menubar,"menuFile")
        self.menuFile2 = makeMenu(self.menubar,"menuFile2")
        self.mainWindow.setMenuBar(self.menubar)

    def __initActions(self):
        """initialises all actions for the main window"""

        def makeAction(name):
            """creates an action and attaches it to the main window"""
            action = QtWidgets.QAction(self.mainWindow)
            action.setObjectName(name)
            return action

        self.actionAbout_Retina = makeAction("actionAbout_Retina")
        self.actionQuit_Retina = makeAction("actionQuit_Retina")
        self.actionPreferences = makeAction("actionPreferences")
        self.actionSettings = makeAction("actionSettings")
        self.actionStart = makeAction("actionStart")

    def __mapActionsToObjects(self):
        """maps actions to different objects on the GUI"""
        self.menuFile.addAction(self.actionAbout_Retina)
        self.menuFile.addAction(self.actionQuit_Retina)
        self.menuFile2.addAction(self.actionSettings)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuFile2.menuAction())
        self.importButton.clicked.connect(self.__importImage)
        self.actionQuit_Retina.triggered.connect(self.mainWindow.close)
        self.actionAbout_Retina.triggered.connect(self.__aboutWindow)
        self.actionSettings.triggered.connect(self.__settings)
        self.clearButton.clicked.connect(self.__clearFiles)
        self.webcamButton.clicked.connect(self.__startWebcam)
        self.stopButton.clicked.connect(self.__stopWebcam)
        self.refreshButton.clicked.connect(self.__refresh)
        self.nextRecognisedButton.clicked.connect(self.__nextFace)
        self.prevRecognisedButton.clicked.connect(self.__prevFace)
        self.nextDetectedButton.clicked.connect(self.__nextDetected)
        self.prevDetectedButton.clicked.connect(self.__prevDetected)
        self.databaseInput.returnPressed.connect(self.__updateDatabase)
        QtCore.QMetaObject.connectSlotsByName(self.mainWindow)

    def __retranslateUi(self):
        """sets the text for all objects in the GUI"""
        _translate = QtCore.QCoreApplication.translate
        self.mainWindow.setWindowTitle(_translate("MainWindow", "Retina - Enhanced Facial Recognition"))
        self.importButton.setText(_translate("MainWindow", "Import Source"))
        self.clearButton.setText(_translate("MainWindow", "Clear Files"))
        self.webcamButton.setText(_translate("MainWindow", "Webcam"))
        self.stopButton.setText(_translate("MainWindow", "Stop"))
        self.refreshButton.setText(_translate("MainWindow", "Refresh GUI"))
        self.facesRecLabel.setText(_translate("MainWindow", "FACES RECOGNISED"))
        self.nextRecognisedButton.setText(_translate("MainWindow", "Next"))
        self.prevRecognisedButton.setText(_translate("MainWindow", "Previous"))
        self.nextDetectedButton.setText(_translate("MainWindow", "Next"))
        self.prevDetectedButton.setText(_translate("MainWindow", "Previous"))
        self.facesRecLabel2.setText(_translate("MainWindow", "Current face:"))
        self.currentFace.setText(_translate("MainWindow", "N/A"))
        self.accuracyLabel.setText(_translate("MainWindow", "Confidence:"))
        self.confidenceLabel.setText(_translate("MainWindow", "N/A"))
        self.loadedLabel.setText(_translate("MainWindow", "Currently Loaded: N/A"))
        self.framelabel.setText(_translate("MainWindow", "Current frame: N/A"))
        self.menuFile.setTitle(_translate("MainWindow", "Retina"))
        self.menuFile2.setTitle(_translate("MainWindow", "More"))
        self.actionAbout_Retina.setText(_translate("MainWindow", "About Retina"))
        self.actionQuit_Retina.setText(_translate("MainWindow", "Quit Retina"))
        self.actionPreferences.setText(_translate("MainWindow", "Preferences"))
        self.actionSettings.setText(_translate("MainWindow", "Settings"))

    def __importImage(self):
        """Import image/video and start detection"""
        self.__faceList = []
        self.__faceGallery = []
        self.framelabel.setText(QtCore.QCoreApplication.translate("MainWindow", "Current frame: Latest"))
        self.__clearFiles()
        self.confidenceLabel.setText(QtCore.QCoreApplication.translate("MainWindow", "N/A"))
        self.currentFace.setText(QtCore.QCoreApplication.translate("MainWindow", "N/A"))
        self.databaseInput.setText("")
        self.databaseInput.setEnabled(True)
        self.importButton.setDisabled(True)
        self.webcamButton.setDisabled(True)
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self.mainWindow, "Open File (*.jpg) (*.png) (.mp4)")
        if filePath is '':
            self.databaseInput.setEnabled(False)
            self.importButton.setDisabled(False)
            self.webcamButton.setDisabled(False)
            self.loadedLabel.setText(QtCore.QCoreApplication.translate("MainWindow", "Currently Loaded: N/A"))
            self.changeDetectedLabel(None)
        else:
            shutil.copy(filePath, INPATH)
            fileName = os.listdir(INPATH)[0]
            if fileName.endswith(".jpg") or fileName.endswith(".png"):
                self.loadedLabel.setText(
                    QtCore.QCoreApplication.translate("MainWindow", "Currently Loaded: " + fileName))
                self.changeDetectedLabel(os.path.join(INPATH, fileName))
                self.forImage = True
                self.__startDetection()
            elif fileName.endswith(".mp4"):
                print("mp4 read")
                self.loadedLabel.setText(
                    QtCore.QCoreApplication.translate("MainWindow", "Currently Loaded: " + fileName))
                self.changeDetectedLabel(os.path.join(INPATH, fileName))
                self.forImage = False
                self.__startDetection()


    def changeDetectedLabel(self, path):
        """Change the image with bound box generated by detection to show in GUI.

        Args:
            path: path of the detected image.
        """
        if (path is None):
            self.dispImageLabel.hide()
        else:
            pixmap = QtGui.QPixmap(path)
            if pixmap.size().width() > pixmap.size().height():
                pixmap = pixmap.scaledToWidth(350)
            else:
                pixmap = pixmap.scaledToHeight(350)

            self.dispImageLabel.setPixmap(pixmap)
            self.dispImageLabel.show()

    def __nextDetected(self):
        """Displays the next boxed faces image in gallery"""
        self.__detSelected = (self.__detSelected + 1) % len(self.__detGallery)
        self.__updateDetSelected()
        self.framelabel.setText(QtCore.QCoreApplication.translate("MainWindow", "Current frame: " + str(self.__detSelected+1) + " / " + str(len(self.__detGallery))))

    def __prevDetected(self):
        """Displays the previous boxed faces image in gallery"""
        self.__detSelected = (self.__detSelected - 1) % len(self.__detGallery)
        self.__updateDetSelected()
        self.framelabel.setText(QtCore.QCoreApplication.translate("MainWindow", "Current frame: " + str(self.__detSelected+1) + " / " + str(len(self.__detGallery))))

    def insertDetected(self, path):
        """Adds an image to the detected gallery and changes the image to match

        Args:
            path: path of the detected image.
        """
        pixmap = QtGui.QPixmap(path)
        if self.getSaveImageToggleFlag():
            self.__detGallery.append(pixmap)
        else:
            if len(self.__detGallery) != 0:
                self.__detGallery[0] = pixmap
            else:
                self.__detGallery.append(pixmap)
        self.__detSelected = len(self.__detGallery) - 1
        self.__updateDetSelected()

    def __updateDetSelected(self):
        """Updates the detected faces label to show the currently selected image from gallery"""
        pixmap = self.__detGallery[self.__detSelected]


        if pixmap.size().width() > pixmap.size().height():
            pixmap = pixmap.scaledToWidth(350)
        else:
            pixmap = pixmap.scaledToHeight(350)
        self.dispImageLabel.setPixmap(pixmap)
        self.dispImageLabel.show()

    def setDetected(self, num):
        """Show the current frame in GUI.

        Args:
            num (int): the number of faces have been detected.
        """

    def __aboutWindow(self):
        """Displays the about page in a new window"""
        self.__about_page.show()

    def __enableAutosave(self):
        """Not implemented"""
        print("enable autosave")

    def __disableAutosave(self):
        """Not implemented"""
        print("disable autosave")

    def __clearFiles(self):
        """Deletes all local files and resets the UI"""
        for f in os.listdir(INPATH):
            filePath = os.path.join(INPATH, f)
            os.unlink(filePath)
        for f in os.listdir(OUTPATH):
            filePath = os.path.join(OUTPATH, f)
            os.unlink(filePath)

        self.setEnabledButtons(False)
        self.databaseInput.setText("")
        self.databaseInput.setEnabled(False)
        self.importButton.setDisabled(False)
        self.webcamButton.setDisabled(False)
        self.loadedLabel.setText(QtCore.QCoreApplication.translate("MainWindow", "Currently Loaded: N/A"))
        self.framelabel.setText(QtCore.QCoreApplication.translate("MainWindow", "Current frame: N/A"))
        self.dispImageLabel.hide()
        self.dispImageLabel2.hide()
        self.__faceSelected = 0
        self.__faceGallery = []
        self.__faceList = []
        self.__detSelected = 0
        self.__detGallery = []

    def addFace(self, face):
        """Add the recognised faces to image gallery in GUI.

        Args:
            face (Utilities.Face): the recognised face.
        """
        self.__faceList.append(face)
        fileName = face.facePath
        filePath = os.path.join(OUTPATH, fileName)

        if not self.getSaveImageToggleFlag():
            filePath = os.path.join(SELFPATH, "default.png")

        self.__faceGallery.append(QtGui.QPixmap(filePath))
        self.__nextFace()

    def __refresh(self):
        """Not implemented"""
        pass


    def __startWebcam(self):
        """Starts detection using the webcam for 10 seconds"""
        self.confidenceLabel.setText(QtCore.QCoreApplication.translate("MainWindow", "N/A"))
        self.__clearFiles()
        self.databaseInput.setText("")
        self.databaseInput.setEnabled(True)
        self.currentFace.setText(QtCore.QCoreApplication.translate("MainWindow", "N/A"))
        self.webcamButton.hide()
        self.stopButton.show()
        self.webcamButton.setDisabled(True)
        self.importButton.setDisabled(True)
        self.framelabel.setText(QtCore.QCoreApplication.translate("MainWindow", "Current frame: Latest"))
        self.loadedLabel.setText(QtCore.QCoreApplication.translate("MainWindow", "Currently Loaded: Webcam"))
        self.forImage = False
        self.startMethod(self, 1)

    def __stopWebcam(self):
        self.stopButton.hide()
        self.webcamButton.show()
        self.stopRecording = True
        
    def __nextFace(self):
        """Displays the next face from gallery"""
        self.__faceSelected = (self.__faceSelected + 1) % len(self.__faceGallery)
        self.__updateFaceSelected()
        self.currentFace.setText(QtCore.QCoreApplication.translate("MainWindow", str(self.__faceSelected+1)+" / "+str(len(self.__faceGallery))))


    def __prevFace(self):
        """Displays the next face from gallery"""
        self.__faceSelected = (self.__faceSelected - 1) % len(self.__faceGallery)
        self.__updateFaceSelected()
        self.currentFace.setText(QtCore.QCoreApplication.translate("MainWindow", str(self.__faceSelected+1)+" / "+str(len(self.__faceGallery))))

    def __updateFaceSelected(self):
        """Updates the recognised face label to show the currently selected face from gallery"""
        pixmap = self.__faceGallery[self.__faceSelected]

        if (pixmap is None):
            self.dispImageLabel2.hide()
        else:
            if pixmap.size().width() > pixmap.size().height():
                pixmap = pixmap.scaledToWidth(350)
            else:
                pixmap = pixmap.scaledToHeight(350)
            self.dispImageLabel2.setPixmap(pixmap)
            self.dispImageLabel2.show()

        currentData = self.__faceList[self.__faceSelected]
        self.databaseInput.setText(currentData.faceName)
        self.confidenceLabel.setText(QtCore.QCoreApplication.translate("MainWindow", str(currentData.confidence) + "%"))

    def __startDetection(self):
        """Starts detection on an image loaded into ./input directory"""
        self.webcamButton.setDisabled(True)
        self.importButton.setDisabled(True)
        self.__faceGallery = []
        self.__faceList = []
        self.__faceSelected = 0
        self.startMethod(self, 0)

    def __updateDatabase(self):
        """Sets the name of a face"""
        name = self.databaseInput.text()
        self.__faceList[self.__faceSelected].faceName = name
        self.recogModel.add_face(name, self.__faceGallery[self.__faceSelected])

    def __settings(self):
        """Open setting page"""
        self.__settings_page.show()
        print("settings")

    def getSRGANToggleFlag(self):
        """If super resolution is enabled.
        
        Returns:
            bool: if super resolution is enabled.
        """
        return self.__settings_page.srToggleflag

    def getSaveImageToggleFlag(self):
        """If super resolution is enabled.

        Returns:
            bool: if super resolution is enabled.
        """
        return self.__settings_page.saveImagesToggleflag

    def saveNameToText(self):
        file = open(OUTPATH+"/nameList.txt", "w")
        result = {}
        for face in self.__faceList:
            if face.confidence >= 75 and face.faceName[0:7] != "Unknown" and (face.faceName not in result or face.confidence > result[face.faceName][0]):
                result[face.faceName] = [face.confidence, 0]
        for face in self.__faceList:
            if face.confidence >= 60 and face.faceName in result:
                result[face.faceName][1] += 1
        count = 0
        for i in result:
            count += result[i][1]
        for i in result:
            result[i][1] = result[i][1]/count * len(result)
        file.write("Total identites: "+str(len(result))+"\n\n")
        for i in result:
            file.write("Name: " + i +"; Highest Confidence Score: "+str(result[i][0])+"; Appearance Frequency: " + str(result[i][1]) + "\n")
        file.close()

    def set_hardware(self, hardware):
        """Set hardware for both super resolution and recognition model.
        
        Args:
            hardware (str): hardware to move models into, GPU/CPU
        """
        if hardware=='CPU':
            hardware = torch.device('cpu')
        else:
            hardware = torch.device('cuda:0')
        self.srganModel.set_hardware(hardware)
        self.recogModel.set_hardware(hardware)
        self.hardware = hardware
    def get_hardware(self):
        return self.hardware

    def set_upscale_factor(self, factor):
        """Set upscale factor which is used by super resolution.

        Args:
            factor (int): value can be 2/4/8, super resolution model will upscale images by this factor.
        """
        self.srganModel.set_upscale_factor(factor)

                

    def setEnabledButtons(self, value):
        self.databaseInput.setReadOnly(not value)
        self.nextDetectedButton.setEnabled(value and (len(self.__detGallery) > 1))
        self.prevDetectedButton.setEnabled(value and (len(self.__detGallery) > 1))
        self.nextRecognisedButton.setEnabled(value and (len(self.__faceGallery) > 1))
        self.prevRecognisedButton.setEnabled(value and (len(self.__faceGallery) > 1))
        self.clearButton.setEnabled(value)
        if value:
            self.framelabel.setText(QtCore.QCoreApplication.translate("MainWindow","Current Frame: " + str(len(self.__detGallery)) + " / " + str(len(self.__detGallery))))
# Test code:

# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     MainWindow = QtWidgets.QMainWindow()
#     ui = Ui_MainWindow()
#     ui.setupUi(MainWindow, test)
#     MainWindow.show()
#     sys.exit(app.exec_())
