import torch
from torch import nn
import math


class Generator(nn.Module):
    """ Generator Class

    Refer to the paper for more information

    Attributes:
        block1: conv+PReLU layers
        res_block2: residual blocks composed of conv+BN+PReLU+conv+BN
        block3: Up-sample blocks composed of conv+PixelShuffle+PReLU

    """
    def __init__(self, upsample_factor):
        """ Inits the Generator and creates all the layers

        Args:
            upsample_factor(int): How large you want to super resolve
        """
        up_factor = int(math.log(upsample_factor, 2))
        super(Generator, self).__init__()
        # Creates a sequence of actions into a block
        self.block1 = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=9, padding=4),
            nn.PReLU()
        )

        # Residual blocks
        res_block2 = []
        # 16 Blocks deep
        for _ in range(16):
            res_block2.append(ResidualBlock(64))
        self.res_block2 = nn.Sequential(*res_block2)

        # Up-sample blocks is how much you upscale it to
        block3 = [UpsampleBlock(64, 2) for _ in range(up_factor)]
        block3.append(nn.Conv2d(64, 3, kernel_size=9, padding=4))
        self.block3 = nn.Sequential(*block3)

    def forward(self, data):
        """ Passed through the generator
        
        Args:
            data(tensor): data to pass to be super resolved
            
        Return:
            data(tensor): tensor of image which has been super resolved
        """
        block1 = self.block1(data)
        block2 = self.res_block2(block1)

        # Skip connection
        return self.block3(block1 + block2)


class Discriminator(nn.Module):
    """ Discriminator Class

    Refer to the paper for more information

    Attributes:
        conv_layer: series of actions performed on the data, difficult to separate into functions.
                    Composed of conv+BN+Leaky_ReLU
        classifier: last 4 layers, composed of Dense+Leaky_ReLU+Dense+Sigmoid

    """
    def __init__(self):
        """ Inits the Discriminator and creates all the layers"""
        super(Discriminator, self).__init__()
        self.conv_layer = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1, stride=1),
            nn.LeakyReLU(0.2),

            nn.Conv2d(64, 64, kernel_size=3, padding=1, stride=2),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2),

            nn.Conv2d(64, 128, kernel_size=3, padding=1, stride=1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2),

            nn.Conv2d(128, 128, kernel_size=3, padding=1, stride=2),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2),

            nn.Conv2d(128, 256, kernel_size=3, padding=1, stride=1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2),

            nn.Conv2d(256, 256, kernel_size=3, padding=1, stride=2),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2),

            nn.Conv2d(256, 512, kernel_size=3, padding=1, stride=1),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2),

            nn.Conv2d(512, 512, kernel_size=3, padding=1, stride=2),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2),
        )

        # Pytorch has nn.Linear as the equivalent to a Dense Layer
        self.classifier = nn.Sequential(
            nn.Linear(512 * 16 * 16, 1024),
            nn.LeakyReLU(0.2),
            nn.Linear(1024, 1)
        )

    def forward(self, data):
        """ Passed through the discriminator
        
        Args:
            data(tensor): data to pass through the discriminator
            
        Return:
            data(tensor): tensor broken down by discriminator
        """
        batch_size = data.size()[0]
        data = self.conv_layer(data)
        # Reshape tensor to have batch_size columns and let it compute a row
        reshaped_data = data.view(batch_size, -1)
        return torch.sigmoid(self.classifier(reshaped_data))


class ResidualBlock(nn.Module):
    """ Residual Block used in the Generator

    Refer to the paper for more information

    Attributes:
        res_block: conv+BN+PReLU+conv+BN
    """
    def __init__(self, channels):
        """ Inits the Residual blocks and creates all the layers """
        super(ResidualBlock, self).__init__()
        self.res_block = nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(channels),
            nn.PReLU(),
            nn.Conv2d(channels, channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(channels)
        )

    def forward(self, data):
        """ Passed through the ResidualBlock
        
        Args:
            data(tensor): data to pass through a block
            
        Return:
            data(tensor): data that has been passed through a block
        """
        residual = self.res_block(data)
        # Skip connection
        return data + residual


class UpsampleBlock(nn.Module):
    """ Upsample Block used in the Generator at the end

    Refer to the paper for more information

    Attributes:
        upsample_blocks: contains conv+pixelshuffle+PReLU layers
    """
    def __init__(self, channels, upsample_factor):
        """ Inits the upsample blocks and creates all the layers """
        super(UpsampleBlock, self).__init__()
        self.upsample_block = nn.Sequential(
            nn.Conv2d(channels, channels * upsample_factor ** 2, kernel_size=3, padding=1),
            # x2 in the paper means up-scale factor not how many times
            nn.PixelShuffle(upsample_factor),
            nn.PReLU()
        )

    def forward(self, data):
        """ Passed through the UpsampleBlock

        Args:
            data(tensor): data to pass through a block

        Return:
            data(tensor): data that has been passed through a block
        """
        upsample = self.upsample_block(data)
        return upsample





