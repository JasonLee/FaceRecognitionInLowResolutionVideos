import cv2

class facialDetectionManager:
    """handles facial detection when given a frame (image)"""

    ARCHITECTURE = "faceDetection/prototype/facialDetection/deploy.prototxt.txt"
    WEIGHTS = "faceDetection/prototype/facialDetection/res10_300x300_ssd_iter_140000.caffemodel"

    def __init__(self):
        self.frame = None
        self.faces = []
        self.minimum_confidence = 0.2
        self.model = cv2.dnn.readNetFromCaffe(facialDetectionManager.ARCHITECTURE, facialDetectionManager.WEIGHTS)

    def setFrame(self, frame):
        """sets the current frame"""
        self.frame = frame

    def locateFaces(self):
        """locates the faces in the frame"""
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
                if confidence_rating > self.minimum_confidence:
                    (startX, startY, endX, endY) = face[3:7]
                    startX = int( max(0, startX * frame_width) )
                    startY = int( max(0, startY * frame_height) )
                    endX = int( min(frame_width, endX * frame_width) )
                    endY = int( min(frame_height, endY * frame_height) )
                    self.faces.append( (startX,startY,endX,endY) )
        # stores the positions of all faces found in the image - as a collection of (x,y,w,h) data.

    def extractFaces(self):
        """crops the faces from the frame and returns them in a list"""
        cropped_faces = []
        for (startX, startY, endX, endY) in self.faces:
            cropped_faces.append( self.frame[startY : endY, startX : endX] )
        return cropped_faces

    def drawBoxAroundFaces(self): # NOTE: this modifies the frame (by adding rectangles around each face)
        """draws a rectangle around each face on the frame, then returns the frame"""
        for (startX, startY, endX, endY) in self.faces:
            cv2.rectangle(self.frame, (startX, startY), (endX, endY), (255, 0, 0), 2)
        return self.frame
