import copy
import os, cv2, sys
from database.FaceData import FaceData

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


class facialDetectionManager:
    ARCHITECTURE = "facialDetection/deploy.prototxt.txt"
    WEIGHTS = "facialDetection/res10_300x300_ssd_iter_140000.caffemodel"

    MINIMUM_CONFIDENCE = 0.2
    OUT_DIR = 'out'
    IN_DIR = 'input'

    def __init__(self, controller, memory):
        self.faces = []
        self.model = cv2.dnn.readNetFromCaffe(facialDetectionManager.ARCHITECTURE, facialDetectionManager.WEIGHTS)
        self.controller = controller
        self.memory = memory

        facialDetectionManager.MINIMUM_CONFIDENCE = self.controller.get_settings().value("Face Detection Confidence", 0,
                                                                                         float)

    def processFrame(self, testForGAN, cv2_to_tensor, input_frame):
        """ Processes a frame by drawing boxes around faces, storing detected faces in the output directory and
        incrementing the number of frames counted.

        Args:
            testForGAN: function that checks if super resolution should be applied to a face.
            cv2_to_tensor: function that converts an OpenCV image into a tensor.
        """
        for cropped_face_data in self.extractFaces(input_frame):

            face_data = cropped_face_data.get_data()
            tensor = cv2_to_tensor(face_data)

            if testForGAN(face_data) and self.controller.get_settings().value("Toggle SR", 1, int) == 1:
                cropped_face_data.set_data(tensor.unsqueeze(0))
                self.memory.ganQueue.put(cropped_face_data)
                self.memory.ganQueueCount.release()
            else:
                cropped_face_data.set_data(tensor.unsqueeze(0))
                self.memory.recogQueue.put(cropped_face_data)
                self.memory.recogQueueCount.release()

    def locateFaces(self, time_of_frame, input_frame):
        """ Locates the faces in the frame and updates the number of faces counted"""

        # NOTE: The network was trained on RGB images, so do not apply it to grayscale images
        # The image is resized to 300x300 since the weights were trained on 300x300 images
        blob = cv2.dnn.blobFromImage(cv2.resize(input_frame, (300, 300)),
                                     1.0,
                                     (300, 300),
                                     (104.0, 177.0, 123.0))
        self.model.setInput(blob)
        detections = self.model.forward()
        self.faces = []
        (frame_height, frame_width) = input_frame.shape[:2]

        for d in detections:
            for i in range(detections.shape[2]):  # for each channel
                face = d[0, i]
                confidence_rating = face[2]
                if confidence_rating > facialDetectionManager.MINIMUM_CONFIDENCE:
                    (startX, startY, endX, endY) = face[3:7]
                    startX = int(max(0, startX * frame_width))
                    startY = int(max(0, startY * frame_height))
                    endX = int(min(frame_width, endX * frame_width))
                    endY = int(min(frame_height, endY * frame_height))

                    face_data = FaceData((startX, startY, endX, endY), time_of_frame)
                    self.faces.append(face_data)
        # stores the positions of all faces found in the image - as a collection of (x,y,w,h) data.
        boxedFaces = self.drawBoxAroundFaces(input_frame)

        path = os.path.join(facialDetectionManager.OUT_DIR, 'CurrentFrame' + '.jpg')
        cv2.imwrite(path, boxedFaces)

        self.controller.set_image_view(path)

        return boxedFaces

    def extractFaces(self, input_frame):
        """ Crops the faces from the frame and returns them in a list.

        Returns:
            images of faces that have been cropped so that the majority of the background is cropped out.
        """
        cropped_faces = []
        for face_data in self.faces:
            (startX, startY, endX, endY) = face_data.get_data()
            cropped_face_data = FaceData(input_frame[startY: endY, startX: endX], face_data.get_time())
            cropped_faces.append(cropped_face_data)
        return cropped_faces

    def drawBoxAroundFaces(self, input_frame):
        """ Modifies the frame by drawing boxes around located faces.

        Returns:
            The updated frame.
        """
        for face_data in self.faces:
            (startX, startY, endX, endY) = face_data.get_data()
            cv2.rectangle(input_frame, (startX, startY), (endX, endY), (0, 0, 255), 1, cv2.LINE_AA)
        return input_frame

    def set_up_video_writer(self, cv2_video_obj, file_name):
        height = int(cv2_video_obj.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(cv2_video_obj.get(cv2.CAP_PROP_FRAME_WIDTH))
        fps_new_video = self.controller.get_settings().value("Video Capture FPS", 0, int)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        return cv2.VideoWriter(facialDetectionManager.OUT_DIR + '/' + file_name, fourcc, fps_new_video, (width, height))
