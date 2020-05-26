import copy
import os, cv2, sys
from database.FaceData import FaceData
sys.path.append("..")
MINIMUM_BICUBIC_RES = 100


def get_resolution(cv2_image):
    """Get height and width of image.
    
    Args:
        cv2_image: an opencv image
    
    Returns:
        the height and width of the cv2_image 
    """
    height, width, _ = cv2_image.shape
    return height, width
def testForBicubic(cv2_image):
    """Looks at the size of the image. If its below 64bits for either axis then its upscaled with Bicubic.

    Args:
        cv2_image: an opencv image.

    Returns:
        bool: if bicubic operation is needed.
    """
    res = get_resolution(cv2_image)
    if (res[0] < MINIMUM_BICUBIC_RES or res[1] < MINIMUM_BICUBIC_RES):
        return True
    return False

class facialDetectionManager:
    """This class handles face detection when given a frame (image).

    Attributes:
        frame: the frame to detect faces in (OpenCV image).
        outdir: the output directory (String).
        faces: the list of faces detected from the frame (List of OpenCV images).
        faces_counted: the number of faces detected so far in an image or video (Integer).
        frames_counted: the number of frames read from a video, or 1 if the source is an image (Integer).
        minimum_confidence: the threshold for face detection, faces detected with a confidence
        greater than or equal to this value will be counted (Decimal).
        model: the face detection model.
        gui: the graphical user interface.
        memory: the object containing data shared with the super resolution and face recognition threads.
    """
    ARCHITECTURE = "facialDetection/deploy.prototxt.txt"
    WEIGHTS = "facialDetection/res10_300x300_ssd_iter_140000.caffemodel"

    MINIMUM_CONFIDENCE = 0.2

    def __init__(self, controller, memory):
        self.frame = None
        self.outdir = 'out'
        self.faces = []
        self.faces_counted = 0
        self.frames_counted = 0
        self.model = cv2.dnn.readNetFromCaffe(facialDetectionManager.ARCHITECTURE, facialDetectionManager.WEIGHTS)
        self.controller = controller
        self.memory = memory
        self.frame_counter = 0
        self.set_detection_confidence()

    def setFrame(self, frame):
        """ Sets the current frame.

        Args:
            frame: the target image to perform facial detection on
        """
        self.frame = frame

    def processFrame(self, testForGAN, cv2_to_tensor):
        """ Processes a frame by drawing boxes around faces, storing detected faces in the output directory and
        incrementing the number of frames counted.

        Args:
            testForGAN: function that checks if super resolution should be applied to a face.
            cv2_to_tensor: function that converts an OpenCV image into a tensor.
        """
        for cropped_face_data in self.extractFaces():

            face_data = cropped_face_data.get_data()
            tensor = cv2_to_tensor(face_data)

            if testForGAN(face_data) and self.controller.get_settings().value("Toggle SR", 1, int) == 1:
                cropped_face_data.set_data(tensor.unsqueeze(0))
                self.memory.ganQueue.push(cropped_face_data)
                self.memory.ganQueueCount.release()
            else:
                cropped_face_data.set_data(tensor.unsqueeze(0))
                self.memory.recogQueue.push(cropped_face_data)
                self.memory.recogQueueCount.release()

    def locateFaces(self, time_of_frame):
        """ Locates the faces in the frame and updates the number of faces counted"""

        # NOTE: The network was trained on RGB images, so do not apply it to grayscale images
        # The image is resized to 300x300 since the weights were trained on 300x300 images
        blob = cv2.dnn.blobFromImage(           cv2.resize(self.frame, (300, 300)),
                                                1.0,
                                                (300, 300),
                                                (104.0, 177.0, 123.0))
        self.model.setInput(blob)
        detections = self.model.forward()
        self.faces = []
        (frame_height, frame_width) = self.frame.shape[:2]
        for d in detections:
            for i in range(detections.shape[2]): #for each channel
                face = d[0,i]
                confidence_rating = face[2]
                if confidence_rating > facialDetectionManager.MINIMUM_CONFIDENCE:
                    (startX, startY, endX, endY) = face[3:7]
                    startX = int( max(0, startX * frame_width) )
                    startY = int( max(0, startY * frame_height) )
                    endX = int( min(frame_width, endX * frame_width) )
                    endY = int( min(frame_height, endY * frame_height) )

                    face_data = FaceData((startX, startY, endX, endY), time_of_frame)
                    self.faces.append(face_data)
                    self.faces_counted += 1
        # stores the positions of all faces found in the image - as a collection of (x,y,w,h) data.
        boxedFaces = self.drawBoxAroundFaces()
        if True:
            path = os.path.join(self.outdir, 'detected' + str(self.frames_counted) + '.jpg')
        else:
            path = os.path.join(self.outdir, 'CurrentFrame' + '.jpg')
        cv2.imwrite(path, boxedFaces)

        self.frame_counter += 1
        self.controller.set_image_view(path)

        return boxedFaces


    def extractFaces(self):
        """ Crops the faces from the frame and returns them in a list.

        Returns:
            images of faces that have been cropped so that the majority of the background is cropped out.
        """
        cropped_faces = []
        for face_data in self.faces:
            (startX, startY, endX, endY) = face_data.get_data()

            cropped_face_data = FaceData(self.frame[startY: endY, startX: endX], face_data.get_time())
            cropped_faces.append(cropped_face_data)
        return cropped_faces

    def drawBoxAroundFaces(self):
        """ Modifies the frame by drawing boxes around located faces.

        Returns:
            The updated frame.
        """
        for face_data in self.faces:
            (startX, startY, endX, endY) = face_data.get_data()
            cv2.rectangle(self.frame, (startX, startY), (endX, endY), (0, 0, 255), 1, cv2.LINE_AA)
        return self.frame

    def set_detection_confidence(self):
        """Sets the minimum confidence that is used by face detection.

        Args:
            confidence (string): value can be 0.2/0.4/0.6/0.8, faces detected with a confidence equal to or above this
                                 value will be processed by the system.
        """

        facialDetectionManager.MINIMUM_CONFIDENCE = self.controller.get_settings().value("Face Detection Confidence", 0, float)
