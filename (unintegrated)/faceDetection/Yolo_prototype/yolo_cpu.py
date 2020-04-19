import argparse
import sys
import os
from PIL import Image
from .yolo.utils import *
from tqdm import tqdm

#####################################################################
parser = argparse.ArgumentParser()
parser.add_argument('--model-cfg', type=str, default='./cfg/yolov3-face.cfg',
                    help='path to config file')
parser.add_argument('--model-weights', type=str,
                    default='./model-weights/yolov3-wider_16000.weights',
                    help='path to weights of model')
parser.add_argument('--input-dir', type=str, default='',
                    help='path to image file directory')
parser.add_argument('--name-list',type=str,default='filenames.txt',
                    help='path to name list')
parser.add_argument('--output-dir', type=str, default='outputs/',
                    help='path to the output directory')
args = parser.parse_args()


# Give the configuration and weight files for the model and load the network
# using them.
# TOM EDIT: Changed arguments for cv2.dnn.readNetFromDarknet DOES NOT WORK // TODO: Ask Luke
net = cv2.dnn.readNetFromDarknet('C:/Users/Tom/Documents/G52GRP/g52grp-32/faceDetection/Yolo_prototype/cfg/yolov3-face.cfg', './model-weights/yolov3-wider_16000.weights')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# TOM EDIT: Changed _main to runYolo
# TOM EDIT: Changed args.input_dir to inPath function argument
# TOM EDIT: Changed args.output_dir to outPath function argument
# TOM EDIT: Changed args.name_list to inPath + "\\faces.txt"
def runYolo(inPath, outPath):
    file = open(inPath + "/faces.txt")
    count = 0
    for x in file.readlines():
        count+=1
    file = open(inPath + "/faces.txt")
    with tqdm(total=count) as pbar:
        for name in file.readlines():
            name = name.strip('\n')


            image = cv2.imread(inPath + "/" + name)
            # Create a 4D blob from a image.
            blob = cv2.dnn.blobFromImage(image, 1 / 255, (IMG_WIDTH, IMG_HEIGHT),
                                         [0, 0, 0], 1, crop=False)

            # Sets the input to the network
            net.setInput(blob)

            # Runs the forward pass to get output of the output layers
            outs = net.forward(get_outputs_names(net))
            # Remove the bounding boxes with low confidence
            faces = post_process(image, outs, CONF_THRESHOLD, NMS_THRESHOLD)
            if(faces):
                i = faces[0]
                region = image[i[1]:i[1]+i[3],i[0]:i[2]+i[0]]
                cv2.imwrite(outPath + "/" + name, region.astype(np.uint8))
            else:
                print(name+" can't be detected.")
            pbar.update(1)

    print("Finished detection: " + str(count) + " faces\n")

# TOM EDIT: Removed _main() clause
