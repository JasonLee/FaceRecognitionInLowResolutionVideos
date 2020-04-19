import glob
from torch.utils.data import Dataset
from PIL import Image
import torchvision.transforms as transforms


class ImageDataset(Dataset):
    """ Creates a dataset with pairs of images (Low Res, High Res)

    Attributes:
        lr_transform(Transforms[]): A series of transformations to create the Low Resolution image
        hr_transform(Transforms[]): A series of transformations to create the High Resolution image
        files(images[]): List of images
    """
    def __init__(self, root, lr_transforms=None, hr_transforms=None):
        """ Inits ImageDataset with both image transformations and a List of Images. """
        self.lr_transform = transforms.Compose(lr_transforms)
        self.hr_transform = transforms.Compose(hr_transforms)
        self.files = sorted(glob.glob(root + '/*.*'))

    def __getitem__(self, index):
        """ Returns a dictionary containing low res and high res image at the index

        Args:
            index(int): index of image you want to get from the directory

        Returns:
            ListOfImages: A list of 2 Images containing Low Res and High Res Images
        """
        img = Image.open(self.files[index % len(self.files)])
        img_lr = self.lr_transform(img)
        img_hr = self.hr_transform(img)
        return {'lr': img_lr, 'hr': img_hr}

    def __len__(self):
        """ Returns length of the dataset

        Returns:
            len(int): length of the dataset
        """
        return len(self.files)
