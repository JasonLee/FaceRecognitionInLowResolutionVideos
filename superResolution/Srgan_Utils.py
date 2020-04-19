import torch
from PIL import Image
from superResolution.model import Generator
import os.path


class superResolutionModel(object):
    """This is the utility class for super resolution system that can be used in software
   
    Args:
        hardware (str): initial hardware to put the generator in.
    """
    def __init__(self, hardware):
        self.__hardware = hardware
        self.__model_name = 'superResolution/generator_4x.pth'
        self.__upscale_factor = 4
        self.__generator = Generator(self.__upscale_factor).eval()
        self.__generator.to(hardware)
        self.__generator.load_state_dict(torch.load(self.__model_name, map_location=hardware))

    def set_upscale_factor(self, scale_factor):
        """ set the upscale factor for images.
            
        Args: 
            scale_factor: gives a number that we should enlarge the image by
        """
        if scale_factor == 'x2':
            self.__upscale_factor = 2
            self.__model_name = "./superResolution/generator_2x.pth"

        elif scale_factor == 'x4':
            self.__upscale_factor = 4
            self.__model_name = "./superResolution/generator_4x.pth"

        elif scale_factor == 'x8':
            self.__upscale_factor = 8
            self.__model_name = "./superResolution/generator_8x.pth"

        else:
            raise Exception('{} is not a upscale factor. Valid options are 2, 4, 8.'.format(scale_factor))
        self.__generator = Generator(self.__upscale_factor).eval()
        self.__generator.to(self.__hardware)
        self.__generator.load_state_dict(torch.load(self.__model_name, map_location=self.__hardware))

    def set_hardware(self, hardware):
        """Move generator to hardware.

        Args:
            hardware (str): hardware to move generator to, CPU/GPU
        """
        self.__hardware = hardware
        self.__generator = self.__generator.to(hardware)

    def super_resolution(self, image):
        """ Takes in a tensor then super resolves it,
        
        Args:
            image: image to be super resolved.

        Returns:
            tensor: super resolved image.
        """
        image = image.to(self.__hardware)
        return self.__generator(image)
