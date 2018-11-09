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
from pathlib import Path
import time

#global object
g_client = None

_CONF_THRESHOLD = 0.5
_NO_OF_ITERATIONS = -1 

_OUTPUT_FOLDER = Path('../data/outputopencv/')

_IMAGE_TAG = "bird"
verbosity = True
_LOG_RESULT = True
_EXPERIMENTNAME = ''
detectedImages = []


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



def processImages(  outputFolder = _OUTPUT_FOLDER,
                    confThreshold = _CONF_THRESHOLD, 
                    numberOfIterations = _NO_OF_ITERATIONS,
                    imageTag = _IMAGE_TAG,
                    logResult = _LOG_RESULT,
                    experimentName = _EXPERIMENTNAME):
    '''
    Process the image and output if it has detected any birds in the images
    outputFolder IMAGE_SRC_FOLDER = Location of image files
    confThreshold CONF_THRESHOLD = Minimum confidence threshold
    numberOfIterations NO_OF_ITERATIONS = Maximum number of images to be searched. set to <0 for all
    imageTag IMAGE_TAG = The tag to be searched for, default = "bird"
    '''
    global detectedImages
    start_time = time.time() 
    TotalBirdsFound = 0

    init()

    FILE_LIST = []
    for file in os.listdir(outputFolder):
        FILE_LIST.append(file)

    for i, imageName in enumerate(FILE_LIST):
        if ((numberOfIterations > 0) and (i > numberOfIterations)):
            break; # come of of the loop
        # Not allowed in python 2.7
        # print('.', end='', flush=True)
        pathToFileInDisk= os.path.join(outputFolder,imageName)
    
        bBirdFound, description, confidenceScore = DetectBirdInImage(pathToFileInDisk,confThreshold, imageTag )
        if (bBirdFound == True):
            TotalBirdsFound = TotalBirdsFound +1
            detectedImages.append({'ImageName':imageName, 'ConfidenceSore':float('{0:.4f}'.format(confidenceScore))})
            if (verbosity == True):
                print("")
                print("Image name = {0}, imageTag = {1} , Confidence Score = {2:0.4f}, Description = {3}".format(imageName, imageTag, confidenceScore, description))


    elapsed_time = time.time() - start_time
    if (logResult == True):
        import datetime
        from  cosmosDB.cosmosDBWrapper import clsCosmosWrapper
        obj = clsCosmosWrapper()
        dictObject ={   'id': str(datetime.datetime.now()),
                        'provider':  __name__,
                        'elapsedTime': elapsed_time,
                        'result - totalNumberOfRecords': len(FILE_LIST),
                        'result - birdFound' : TotalBirdsFound,
                        'param - confThreshold' : confThreshold, 
                        'param - numberOfIterations' : numberOfIterations,
                        'param - imageTag' : imageTag,
                        'detectedItems': detectedImages
                    }
        obj.logExperimentResult(collectionName = experimentName, documentDict= dictObject)

    return TotalBirdsFound 

if __name__ == "__main__":
    processImages()









