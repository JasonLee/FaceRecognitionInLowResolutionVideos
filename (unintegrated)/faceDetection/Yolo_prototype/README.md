## This is a face detection model using yolov3

## Dependencies
+ opencv-python
+ opencv-contrib-python
+ Numpy
+ Keras
+ Tensorflow
+ Matplotlib
+ Pillow
+ tqdm (optional, can delete tqdm part)

## To use
+ run ```./get-models.sh``` to get weights of network
+ run ```python yolo_cpu.py``` or ```python yolo_gpu.py```

## Argument
+ ``` --input-dir ``` directory of input pictures.
+ ``` --output-dir ``` directory of output faces.
+ ``` --name-list ``` file contains names of all pictures you want to process.

This prototype will be changed a lot due to the requirment and API of other parts, it's now hard coded for convenience of processing our dataset.

This prototype is based on [sthanhng/yoloface](https://github.com/sthanhng/yoloface)
Thanks a lot for Thanh's great work.
