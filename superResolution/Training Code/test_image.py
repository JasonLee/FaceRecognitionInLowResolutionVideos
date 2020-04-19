import argparse
import torch

from PIL import Image
from model import Generator
from torch.autograd import Variable
from torchvision.transforms import ToTensor
from torchvision.utils import save_image

import os.path

# converts to the tensor then saves the image
def process_image_save(filepath):
    """ Pass in a file name, it is then opened, super resolved then saved in the same directory as a png file

    Args:
        filepath(str): file path of the image to be super resolved

    Return:
        generator(image)(tensor): returns the tensor of the super resolved image
        """
    image = Image.open(filepath)
    image = Variable(ToTensor()(image))
    with torch.no_grad():
        image = image.unsqueeze(0)

    if HARDWARE_MODE == 'GPU':
        image = image.cuda()

    return generator(image)

# changes the name of a variable to the right file path
def change_name(image_name):
    """ alters a file name string to remove its file type and replaces it with .png

    Args:
        image_name(str): file path of the image

    Returns:
        image_name(str): modified version of the filepath to represent new file.
        In the format of 'our_SR_FILENAME.png'
    """
    base = os.path.splitext(image_name)[0]
    image_name = 'out_SR_' + base + '.png'
    return image_name

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test Single Image')
    parser.add_argument('--upscale_factor', default=4, type=int, choices=[2 ,4 ,8], help='super resolution upscale factor')
    parser.add_argument('--test_mode', default='GPU', type=str, choices=['GPU', 'CPU'], help='using GPU or CPU')
    parser.add_argument('--image_name', type=str, help='test low resolution image name')
    parser.add_argument('--model_name', default='generator_4x.pth', type=str, help='generator model epoch name')
    opt = parser.parse_args()

    UPSCALE_FACTOR = opt.upscale_factor
    IMAGE_NAME = opt.image_name
    MODEL_NAME = opt.model_name
    HARDWARE_MODE = opt.test_mode

    # Makes sure the Generator is in evaluation mode not training mode
    generator = Generator(UPSCALE_FACTOR).eval()

    if HARDWARE_MODE == 'GPU':
        if not torch.cuda.is_available():
                raise Exception('Cannot use a GPU as CUDA is not available')
        print('GPU is selected, CUDA is avaiable')
        generator = generator.cuda()
        generator.load_state_dict(torch.load('models/' + MODEL_NAME))
    else:
        if torch.cuda.is_available():
            print('You have a GPU available, GPU is preferred due to better perfomance')
        print('CPU is selected')
        generator.load_state_dict(torch.load('models/' + MODEL_NAME, map_location=lambda storage, loc: storage))



    out = process_image_save(IMAGE_NAME)

    save_image(out, change_name(IMAGE_NAME), normalize=True)


