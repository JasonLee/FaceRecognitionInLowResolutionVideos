from PIL import Image
import cv2

def cv2_image_to_pil_image(cv2_image):
    """takes a cv2 image and returns a PIL image"""
    rgb_image = cv2.cvtColor(cv2_image,cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(rgb_image)
    return pil_im