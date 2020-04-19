from __future__ import print_function, division
import os
import torch
import pandas as pd
from skimage import io, transform
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils
import random
import model
from torch.autograd import Variable

class FaceDataset(Dataset):
    def __init__(self, csv_file,root_dir, forTrain, transform = None):
        self.image_name = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.transform = transform
        self.forTrain = forTrain
        if forTrain:
            self.labelSet = {}
            for idx in range(len(self.image_name)):
                i = self.image_name.iloc[idx,0]
                name, label = i.split(' ')
                if(not label in self.labelSet):
                    self.labelSet[label] = [name]
                else:
                    self.labelSet[label].append(name)

    def __len__(self):
        return len(self.image_name)
    def __getitem__(self, idx): # TODO: Change item selecting.
        if self.forTrain:
            anchor_name = os.path.join(self.root_dir, self.image_name.iloc[idx,0].split(' ')[0])
            anchor = io.imread(anchor_name)
            label = self.image_name.iloc[idx,0].split(' ')[1]
            positive_name = anchor_name
            count = 0
            while anchor_name == positive_name:
                count+=1
                positive_name = np.random.choice(self.labelSet[label])
                if count == 10:
                    break
            positive = io.imread(os.path.join(self.root_dir, positive_name))
            index_neg = random.randint(0,len(self)-1)
            while(self.image_name.iloc[index_neg,0].split(' ')[1]==label):
                index_neg = random.randint(0,len(self)-1)
            negative = io.imread(os.path.join(self.root_dir, self.image_name.iloc[index_neg,0].split(' ')[0]))
            if self.transform:
                anchor = self.transform(anchor)
                positive = self.transform(positive)
                negative = self.transform(negative)
            return anchor, positive, negative

        else:
            sample = io.imread(os.path.join(self.root_dir, self.image_name.iloc[idx,0].split(' ')[0]))
            label = self.image_name.iloc[idx,0].split(' ')[1]
            if self.transform:
                sample = self.transform(sample)
            return sample,label

class ToTensor(object):
    def __call__(self,sample):
        image = sample
        image = image.transpose((2,0,1))
        return image


class Rescale(object):
    """Rescale the image in a sample to a given size.

    Args:
        output_size (tuple or int): Desired output size. If tuple, output is
            matched to output_size. If int, smaller of image edges is matched
            to output_size keeping aspect ratio the same.
    """

    def __init__(self, output_size):
        assert isinstance(output_size, list)
        self.output_size = output_size

    def __call__(self, image):
        return transform.resize(image, (self.output_size[0], self.output_size[1]))


class FaceDatasetOrganised(Dataset):
    def __init__(self,root_dir, forTrain, transform = None):
        self.root_dir = root_dir
        self.transform = transform
        self.forTrain = forTrain
        self.labelSet = {}
        self.normalSet = []
        labels = os.listdir(root_dir)
        for label in labels:
            faces = os.listdir(root_dir+'/'+label)
            self.labelSet[label] = faces[:]
            for i in range(len(faces)):
                faces[i] = [faces[i], label]
            self.normalSet.extend(faces)

    def __len__(self):
        return len(self.normalSet)
    def __getitem__(self, idx): # TODO: Change item selecting.
        if self.forTrain:
            label = self.normalSet[idx][1]
            anchor_name = self.normalSet[idx][0]
            anchor = io.imread(self.root_dir + '/' + label + '/' + anchor_name)
            positive_name = anchor_name
            count = 0
            while anchor_name == positive_name:
                count+=1
                positive_name = np.random.choice(self.labelSet[label])
                if count == 10:
                    break
            positive = io.imread(self.root_dir + '/' + label + '/' + positive_name)
            index_neg = random.randint(0,len(self)-1)
            while(self.normalSet[index_neg][1] == label):
                index_neg = random.randint(0,len(self)-1)
            negative = io.imread(self.root_dir + '/' + self.normalSet[index_neg][1] + '/' + self.normalSet[index_neg][0])
            if self.transform:
                anchor = self.transform(anchor)
                positive = self.transform(positive)
                negative = self.transform(negative)
            return anchor, positive, negative

        else:
            sample = io.imread(self.root_dir + '/' + self.normalSet[idx][1] + '/' + self.normalSet[idx][0])
            label = self.normalSet[idx][1]
            if self.transform:
                sample = self.transform(sample)
            return sample,label

    def buildBaseLine(self, net):
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        result = {}
        for label in self.labelSet:
            image = self.transform(io.imread(self.root_dir + '/' + label + '/' + np.random.choice(self.labelSet[label])))
            image = np.expand_dims(image, axis=0)
            image = Variable(torch.from_numpy(image).float(), requires_grad=False)
            image.to(device)
            result[label] = net(image).data
        return result
