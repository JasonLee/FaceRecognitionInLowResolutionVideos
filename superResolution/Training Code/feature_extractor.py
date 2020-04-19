from torch import nn
from torchvision.models.vgg import vgg19


# Pass images through VGG19 Network
class FeatureExtractor(nn.Module):
    """ Passes an image through a VGG19 Network (feature extractor)

    Attributes:
        feature_extractor: contains the vgg19 network
    """
    def __init__(self):
        """ Init the FeatureExtractor """
        super(FeatureExtractor, self).__init__()
        vgg = vgg19(pretrained=True)
        feature_extractor = nn.Sequential(*list(vgg.features)[:12]).eval()
        for param in feature_extractor.parameters():
            param.requires_grad = False
        self.feature_extractor = feature_extractor
        
    def forward(self, images):
        """ Pass image through the VGG19 Network

        Args:
            images(tensor): image tensor

        Returns:
            image(tensor): returns a tensor that has been passed through the VGG19 Network
        """
        return self.feature_extractor(images)


# Necessary for running on windows. Prevents recursion
if __name__ == "__main__":
    featureExtractor = FeatureExtractor()