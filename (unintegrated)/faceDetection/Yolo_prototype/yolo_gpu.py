import argparse

from yolo.yolo import YOLO, detect_video, detect_img


#####################################################################
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='model-weights/YOLO_Face.h5',
                        help='path to model weights file')
    parser.add_argument('--anchors', type=str, default='cfg/yolo_anchors.txt',
                        help='path to anchor definitions')
    parser.add_argument('--classes', type=str, default='cfg/face_classes.txt',
                        help='path to class definitions')
    parser.add_argument('--score', type=float, default=0.5,
                        help='the score threshold')
    parser.add_argument('--iou', type=float, default=0.45,
                        help='the iou threshold')
    parser.add_argument('--img-size', type=list, action='store',
                        default=(416, 416), help='input image size')
    parser.add_argument('--name-list', type=str, default='filenames.txt',
                        help='image detection mode')
    parser.add_argument('--input-dir', type=str, default='/data/psywp1/celeba',
                        help='path to the video')
    parser.add_argument('--output-dir', type=str, default='/data/psywp1/celeba_output',
                        help='image/video output path')
    args = parser.parse_args()
    return args


def _main():
    # Get the arguments
    args = get_args()

    # Image detection mode
    YOLO(args).detect_image_new()


    print('==> All done!')
    print('***********************************************************')

if __name__ == "__main__":
    _main()
