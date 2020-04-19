from test import *
import warnings
import argparse
warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser(description='Main function for training and testing')
parser.add_argument('--single_directory', default=False, type=bool, help='Use a single directory and name lists or two organised directories without name lists')
parser.add_argument('--enable_training', default=True, type=bool, help='do training with testing or just testing')
parser.add_argument('--resume_training', default=True, type=bool, help='import trained model and resume training, only useful when training is enabled.')
parser.add_argument('--train_dir', default='/data/psywp1/train_crop', type=str, help='organised directory for training')
parser.add_argument('--test_dir', default='/data/psywp1/test_crop', type=str, help='organised directory for testing')
parser.add_argument('--image_dir', default='/data/psywp1/celebA', type=str, help='unorganised directory for training and testing')
parser.add_argument('--train_list', default='~/small_train.txt', type=str, help='name list contains picutres names and lables for training')
parser.add_argument('--test_list', default='~/small_test.txt', type=str, help='name list contains picutres names and lables for testing')
parser.add_argument('--batch_size', default=80, type=int, help='batch size of 80 need 9.2GB, reduce it if program crashes')
parser.add_argument('--model_name', default="VGGLargeModel.pt", type=str, help='model file to use for saving, importing')
parser.add_argument('--epoch', default=10, type=int, help='how many epoch to train on the whole training dataset')
parser.add_argument('--learning_rate', default=0.00005, type=float, help='learning for the optimizer')
parser.add_argument('--dynamic_lr', default=True, type=bool, help='if the program is allowed to change learning rate dynamically')

args = parser.parse_args()


if __name__ == '__main__':
    if args.enable_training:
        runTrain(args)
    runTest(args)
