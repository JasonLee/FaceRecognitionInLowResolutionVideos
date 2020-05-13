Master: [![Build Status](https://travis-ci.org/JasonLee/FaceRecognitionInLowResolutionVideos.svg?branch=master)](https://travis-ci.org/JasonLee/FaceRecognitionInLowResolutionVideos)       Dev: [![Dev Build Status](https://travis-ci.org/JasonLee/FaceRecognitionInLowResolutionVideos.svg?branch=dev)](https://travis-ci.org/JasonLee/FaceRecognitionInLowResolutionVideos)
# Facial Recognition from Low Quality Videos

This project is aimed to improve face recognition in low resolution videos through Face Detection, Super Resolution then using the upscaled face image in the face recognition. ML components are written using Pytorch and OpenCV. 

This was originally my 2nd Year Group Project from https://github.com/pwz266266/VideoFacRec (imported from GitLab)
Project was revived and rewritten by myself. 

## Links
+ Original write-ups: https://drive.google.com/drive/folders/1YhIltgKVwol4yVnlCcrE3m35y1TZ-UKy?usp=sharing
+ TODO Links to model files, public Trello

## Environment Setup
+ Install miniconda3 from https://docs.conda.io/en/latest/miniconda.html. You can follow the instructions here to create a new env in the anaconda prompt
+ Activate your environment with ````conda activate ...````
+ Running ````pip install -r requirements.txt```` should install all the dependencies.
+ If you have a NVIDIA GPU you can install the CUDA toolkit https://developer.nvidia.com/cuda-downloads

## Running 
+ run ````python start.py```` in the anacona prompt.
+ TODO Add instructions to add new faces (future feature).

## Branching Strategy
+ There will be 2 main branches: **Master** and **Dev**. **Master** should always be working and deployable. **Dev** will contain completed features and any single commit hotfixes.
+ Features will branched off Dev. Pull requests should be made to request in merging of code. 
+ Requirements of PRs are that:
    + Commits should be squashed
    + Commit messages should be helpful
    + Code written should be tested
    + Travis builds should be green.
+ PRs should be peer reviewed when possible