#!/usr/bin/env python

# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Imports the Google Cloud client library
# [START vision_python_migration_import]
from google.cloud import vision
from google.cloud.vision import types
import io
import os

#global object
g_client = None

_CONF_THRESHOLD = 0.5
_NO_OF_ITERATIONS = -1 
_IMAGE_SRC_FOLDER = '..\\Data\\outputOpenCV\\'
_IMAGE_TAG = "bird"
verbosity = True

def init():
    # [END vision_python_migration_import]
    # Instantiates a g_client
    # [START vision_python_migration_client]
    global g_client
    g_client = vision.ImageAnnotatorClient()


def DetectBirdInImage( pathToFileInDisk,confThreshold, imageTag):
    global g_client
    assert(g_client is not None), "Invoke init before calling run"
    bRV = False
     # Loads the image into memory
    with io.open(pathToFileInDisk, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    # Performs label detection on the image file
    response = g_client.label_detection(image=image)
    labels = response.label_annotations

    for label in labels:
        if ((label.description == imageTag) and (label.score > confThreshold)):
            return True, label.description, label.score

    return bRV, "", ""



def processImages(  imageSrcFolder = _IMAGE_SRC_FOLDER,
                    confThreshold = _CONF_THRESHOLD, 
                    numberOfIterations = _NO_OF_ITERATIONS,
                    imageTag = _IMAGE_TAG):
    '''
    Process the image and output if it has detected any birds in the images
    imageSrcFolder IMAGE_SRC_FOLDER = Location of image files
    confThreshold CONF_THRESHOLD = Minimum confidence threshold
    numberOfIterations NO_OF_ITERATIONS = Maximum number of images to be searched. set to <0 for all
    imageTag IMAGE_TAG = The tag to be searched for, default = "bird"
    '''
    TotalBirdsFound = 0

    init()

    FILE_LIST = []
    for file in os.listdir(imageSrcFolder):
        FILE_LIST.append(file)

    for i, imageName in enumerate(FILE_LIST):
        if ((numberOfIterations > 0) and (i > numberOfIterations)):
            break; # come of of the loop
        # Not allowed in python 2.7
        # print('.', end='', flush=True)
        pathToFileInDisk= imageSrcFolder+ imageName
    
        bBirdFound, description, confidenceScore = DetectBirdInImage(pathToFileInDisk,confThreshold, imageTag )
        if (bBirdFound == True):
            TotalBirdsFound = TotalBirdsFound +1
            if (verbosity == True):
                print("")
                print("Image name = {0}, imageTag = {1} , Confidence Score = {2:0.4f}, Description = {3}".format(imageName, imageTag, confidenceScore, description))


    return TotalBirdsFound 

#processImages()           









