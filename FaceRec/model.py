# -*- coding: utf-8 -*-
"""This module is used to define network structure used by face recognition system.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torchvision.models import resnet34

class FaceNetModel(nn.Module):
    """This class defines resnet34 network based on the original resnet34 introduced by this paper: https://arxiv.org/abs/1512.03385.

    Attributes:
        model: the original resnet34 model.
    """
    def __init__(self): #num_classes
        super (FaceNetModel, self).__init__()
        self.model            = resnet34(False)
        self.model.fc         = nn.Linear(25088, 100)


    def __l2_norm(self, input):
        input_size = input.size()
        buffer     = torch.pow(input, 2)
        normp      = torch.sum(buffer, 1).add_(1e-10)
        norm       = torch.sqrt(normp)
        _output    = torch.div(input, norm.view(-1, 1).expand_as(input))
        output     = _output.view(input_size)

        return output


    def forward(self, x):
        """Process input use this network

        Args:
            x (tensor): input to be processed.

        Returns:
            output of network
        """
        if self.__device == torch.device('cpu'):
            x = x.type('torch.FloatTensor')
        else:
            x = x.type('torch.cuda.FloatTensor')
        x = self.model.conv1(x)
        x = self.model.bn1(x)
        x = self.model.relu(x)
        x = self.model.maxpool(x)
        x = self.model.layer1(x)
        x = self.model.layer2(x)
        x = self.model.layer3(x)
        x = self.model.layer4(x)
        x = x.view(x.size(0), -1)
        x = self.model.fc(x)

        x = self.__l2_norm(x)
        # Multiply by alpha = 10 as suggested in https://arxiv.org/pdf/1703.09507.pdf
        alpha         = 10
        x = x*alpha

        return x

    def to(self, device):
        """Move the network to specific device, override the original

        Args:
            device (str): the device to move to (cpu/gpu)

        Returns:
            Moved model
        """
        output = super(FaceNetModel,self).to(device)
        output.__device = device
        output.model = output.model.to(device)
        return output
