# -*- coding: utf-8 -*-
"""This module defines utility class for face recognition system that can be used in software"""
import warnings
from FaceRec.DatabaseManagement import *
from FaceRec.model import *
from torchvision import transforms
from skimage import transform
import random
warnings.filterwarnings("ignore")


class recognitionModel(object):
    """This is the utility class for face recognition system that can be used in software
   
    Args:
        database (str): path of database root directory
        hardware (str): initial hardware to put the network in.
    """
    def __init__(self, database, hardware):
        self.__database_path = database
        self.__database = Database(database)
        self.__hardware = hardware
        self.__model = FaceNetModel()
        self.__model.load_state_dict(torch.load("./FaceRec/FaceRecModel.pth",map_location=hardware))
        self.__model.eval()
        self.__model.to(hardware)
        self.__buildBaseLine()

    def add_face(self, identity, face):
        self.__database.saveImage(identity, str(random.randint(1,1000)), face)
        self.__database = Database(self.__database_path)
        self.__buildBaseLine()

    def __buildBaseLine(self):
        self.__composed = transforms.Compose([Rescale([224,224]), transforms.ToTensor()])
        self.__baseline = {}

        #Build the baseline for recognition system
        names = self.__database.getNames()
        for name in names:
            images = self.__database.getImages(name)
            count = 0
            result = 0
            for image in images:
                count+=1
                image = self.__composed(image)[None,:,:,:]
                result += self.__model(torch.autograd.Variable(image)).data
            self.__baseline[name] = result/count

        self.__composed = torch.nn.Upsample([224,224])

    def recognize(self, face):
        """Recognize a face using this model
       
        Args:
            face (tensor): the face to be recognized.
      
        Returns:
            A integer which represent the confidence score of recognition.
            A label that the face is recognized as.
        """
        face = self.__composed(face)
        face = face.to(self.__hardware)
        output = self.__model(torch.autograd.Variable(face)).data
        label = ''
        distance = 100
        for i in self.__baseline:
            currDis = (output - self.__baseline[i]).pow(2).sum(1)
            if(currDis < distance):
                distance = currDis
                label = i
        distance = float(distance)
        if(distance >= 12):
            confidence = 0
        elif(distance <= 1):
            confidence = 100
        else:
            confidence = (12 - distance)/11*100
        return int(confidence), label

    def set_hardware(self, hardware):
        """set the hardware of recognition model.
       
        Args:
            hardware (str): the hardware to move network to.
        """
        self.__hardware = hardware
        self.__model = self.__model.to(hardware)
        newBaseline = {}
        for i in self.__baseline:
            if self.__hardware == torch.device('cpu'):
                newBaseline[i] = self.__baseline[i].type('torch.FloatTensor')
            else:
                newBaseline[i] = self.__baseline[i].type('torch.cuda.FloatTensor')
        self.__baseline = newBaseline
class Rescale(object):
    """Callable class, used to rescale a 2D list/image.
    
    Args:
        output_size: a list contains two integers.
   
    Attributes:
        output_size: size of output list/image.
    """
    def __init__(self, output_size):
        assert isinstance(output_size, list)
        self.output_size = output_size

    def __call__(self, image):
        """Rescale an image
       
        Args:
            image: image to rescale
       
        Returns:
            rescaled list/image.
        """
        return transform.resize(image, (self.output_size[0], self.output_size[1]))
