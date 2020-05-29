Master: [![Build Status](https://travis-ci.org/JasonLee/FaceRecognitionInLowResolutionVideos.svg?branch=master)](https://travis-ci.org/JasonLee/FaceRecognitionInLowResolutionVideos)       Dev: [![Dev Build Status](https://travis-ci.org/JasonLee/FaceRecognitionInLowResolutionVideos.svg?branch=dev)](https://travis-ci.org/JasonLee/FaceRecognitionInLowResolutionVideos)
# Facial Recognition from Low Quality Videos

This project is aimed to improve face recognition in low resolution videos through Face Detection, Super Resolution then using the up-scaled face image in the face recognition. ML components are written using Pytorch and OpenCV. 

This was originally my 2nd Year Group Project from https://github.com/pwz266266/VideoFacRec (imported from GitLab Private Repo)
Project was revived and rewritten by myself. 

## Links
+ Original write-ups: [Google Drive Report](https://drive.google.com/drive/folders/1YhIltgKVwol4yVnlCcrE3m35y1TZ-UKy?usp=sharing)
+ Model files: [Google Drive Link](https://drive.google.com/drive/folders/1haN4myJ2z2_ffArshHIZu7kOlHye0lGE?usp=sharing)

## Environment Setup
+ Install miniconda3 from [Link](https://docs.conda.io/en/latest/miniconda.html). You can follow the instructions here to create a new env in the anaconda prompt
+ Activate your environment with ````conda activate ...````
+ Running ````pip install -r requirements.txt```` should install all the dependencies into your env.
+ If you have a NVIDIA GPU you can install the CUDA toolkit [here](https://developer.nvidia.com/cuda-downloads)

## Running 
+ Drag each model file from into their respective folder - [Google Drive Link](https://drive.google.com/drive/folders/1haN4myJ2z2_ffArshHIZu7kOlHye0lGE?usp=sharing)
+ Run ````python start.py```` in the anaconda prompt to start.
+ Adding images - You can process an image and on the list click the modify button and add a name. Or you can manually make a new folder in ````images/```` with the name and add images.

## Testing
+ Run tests with ````python -m unittest````
+ Travis CI pipeline is [here](https://travis-ci.com/github/JasonLee/FaceRecognitionInLowResolutionVideos)

## Branching Strategy
+ There will be 2 main branches: **Master** and **Dev**. **Master** should always be working and deployable. **Dev** will contain completed features and any single commit hotfixes.
+ Features will branched off Dev. Pull requests should be made to request in merging of code. 
+ Requirements of PRs are that:
    + Commits should be squashed
    + Commit messages should be helpful
    + Code written should be tested
    + Travis builds should be green.
+ PRs should be peer reviewed when possible

## Common Issues
1. ERROR: DirectShowPlayerService::doRender: Unresolved error code 0x80040266 (IDispatch error #102)

    Solution: Video player is missing a codec. Install k-lite codec pack link is [here](https://codecguide.com/download_k-lite_codec_pack_basic.htm)

2. ERROR: Out of Memory Issues when using GPU/CPU

    Solution: Super resolution has a high GPU/CPU memory usage when used on high resolution images already. It was restricted to be use only on smaller images.
    So not much can be done. You would need to disable it in the settings.

