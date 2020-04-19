### This file is used to track progress of face recognition part.

## Current Stage:
+ All basic coding job is done, training the network to get a usable model.
+ Have already get high accurate face detection model, wait all pictures to be processed.

## Todo:
+ Get a high accuracy model.

## Notes:
+ use command `python main.py` to run face recognition with siamese network prototype.
+ Command line parameters can be found in main.py file.
+ For more information, please refer to [Documentation for face recognition](https://docs.google.com/document/d/1ewgdp05EgApf3z1Pm-swjOzYhsgC0gym_dkNjnN5hmo/edit?usp=drive_web&ouid=111796135684734564072)

If program crashes, try to reduce `BATCH_SIZE`, require roughly 11G memory for BATCH_SIZE=130.

## Dependency
+ python 3.*
+ pytorch 1.0
+ torchvision
+ matplotlib
+ skimage
+ numpy
+ pandas

## Current Results:
### The program has high accuracy when deal with small dataset (85%+ accuracy)
### For large dataset (200k+ pictures), get 30% accuracy
### See config.txt for more details, the testing result is provided by VGGface2 test set.
