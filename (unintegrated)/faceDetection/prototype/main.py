import cv2
from facialDetection.webcamFDM import webcamFDM
from dbManagement.fileManager import fileManager
from faceDetToSuperRes import cv2_image_to_pil_image

MINIMUM_RESOLUTION = 100
DATABASE_DIRECTORY = "detected"
FM = fileManager( DATABASE_DIRECTORY )
FDM = webcamFDM()
CAM = cv2.VideoCapture(0)

def get_resolution(cv2_image):
    """takes a cv2 image and returns its resolution: height, width"""
    height, width, _ = cv2_image.shape
    return height, width

def sendToDatabase(f):
    """stores a given face in the face database"""
    label = "frame" + str(FM.getSizeOfDB())
    FM.insertIntoDB(label, f)

while cv2.waitKey(1) != ord(" "):  # while the space button is not pressed
    FDM.run(CAM)
    for f in FDM.extractFaces():
        res = get_resolution(f)
        if res[0] < MINIMUM_RESOLUTION or res[1] < MINIMUM_RESOLUTION:
            print("SUPER RESOLVE IMAGE") # f = superResolve(f)
        sendToDatabase(f)
    cv2.imshow('frame', FDM.drawBoxAroundFaces())

CAM.release()
cv2.destroyAllWindows()


