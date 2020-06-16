"""This file defines several utility functions used by software.

Attributes:
    MINIMUM_BICUBIC_RES (int): minimum image resolution that doesn't need to be processed by bicubic operation.
    MINIMUM_GAN_RES (int): minimum image resolution that doesn't need to be processed by super resolution.
"""
import cv2
from PIL import Image
from torch.autograd import Variable
from torchvision.transforms import ToTensor

MINIMUM_BICUBIC_RES = 50
MINIMUM_GAN_RES = 100

class Face:
    """This class defines face data structure used to store recognized faces.

    Args:
        facePath (str): Path of the image file.
        faceName (str): Label of the image, identity's name or 'Unknown'.
        confidence (int): Confidence score for recognized face.

    Attributes:
        facePath (str): Path of the image file.
        faceName (str): Label of the image, identity's name or 'Unknown'.
        confidence (int): Confidence score for recognized face.
    """
    def __init__(self, facePath, faceName, confidence):
        self.facePath = facePath
        self.faceName = faceName
        self.confidence = confidence

def get_resolution(cv2_image):
    """Get height and width of image.
    
    Args:
        cv2_image: an opencv image
    
    Returns:
        the height and width of the cv2_image 
    """
    height, width, _ = cv2_image.shape
    return height, width

def cv2_to_tensor(cv2_image):
    """Convert a cv2 image to tensor.
    
    Args:
        cv2_image : an opencv image.
    
    Returns:
        tensor: converted image.
    """
    rgb_im = cv2.cvtColor(cv2_image,cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(rgb_im)

    tensor = Variable(ToTensor()(pil_im))
    return tensor

def testForGAN(cv2_image):
    """ Test if image resolution is smaller than threshold for super resolution.

    Args:
        cv2_image : an opencv image of a face

    Returns:
        bool: if super resolution is needed.
    """
    res = get_resolution(cv2_image)
    if (res[0] < MINIMUM_GAN_RES or res[1] < MINIMUM_GAN_RES):
        return True
    return False
