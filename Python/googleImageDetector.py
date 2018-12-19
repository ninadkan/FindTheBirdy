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

import common 

import azureFS.azureFileShareTest as fs
import azureFS.mask_creation as mask
#global object
g_client = None

_CONF_THRESHOLD = 0.5
_NO_OF_ITERATIONS = -1 

verbosity = True
_LOG_RESULT = True
_EXPERIMENTNAME = ''
g_detectedImages = []


def init():
    # [END vision_python_migration_import]
    # Instantiates a g_client
    # [START vision_python_migration_client]
    global g_client
    g_client = vision.ImageAnnotatorClient()


def DetectBirdInImage( outputFolder,imageName,confThreshold, imageTag):
    global g_client
    assert(g_client is not None), "Invoke init before calling run"
    bRV = False
     # Loads the image into memory

    content = None
    if (common._FileShare == False):
        with io.open(os.path.join(outputFolder,imageName), 'rb') as image_file:
            content = image_file.read()
    else:
        brv, desc, content = mask.GetRawImageAsBytes(common._FileShareName, outputFolder, imageName)
        assert(brv == True), "Error Get Raw Image" + imageName

    
    assert(content is not None), "Unable to read image file " + imageName

    image = types.Image(content=content)

    # Performs label detection on the image file
    response = g_client.label_detection(image=image)
    labels = response.label_annotations

    for label in labels:
        if ((label.description == imageTag) and (label.score > confThreshold)):
            return True, label.description, label.score

    return bRV, "", ""



def processImages(  outputFolder = common._SRCIMAGEFOLDER,
                    confThreshold = _CONF_THRESHOLD, 
                    numberOfIterations = _NO_OF_ITERATIONS,
                    imageTag = common._IMAGE_TAG,
                    logResult = _LOG_RESULT,
                    experimentName = _EXPERIMENTNAME):
    '''
    Process the image and output if it has detected any birds in the images
    outputFolder IMAGE_SRC_FOLDER = Location of image files
    confThreshold CONF_THRESHOLD = Minimum confidence threshold
    numberOfIterations NO_OF_ITERATIONS = Maximum number of images to be searched. set to <0 for all
    imageTag IMAGE_TAG = The tag to be searched for, default = "bird"
    '''
    global g_detectedImages
    g_detectedImages = []
    start_time = time.time() 
    TotalBirdsFound = 0

    init()

    FILE_LIST = []
    if (common._FileShare == False):
        outputFolder = os.path.join(outputFolder,experimentName)
        outputFolder = os.path.join(outputFolder,common._DESTINATIONFOLDER)
        for file in os.listdir(outputFolder):
            FILE_LIST.append(file)
    else:
        outputFolder = outputFolder + "/" + experimentName
        outputFolder = outputFolder + "/" + common._DESTINATIONFOLDER
        brv, desc, lst = fs.getListOfAllFiles(common._FileShareName, outputFolder)
        if (brv == True):
            for i, imageFileName in enumerate(lst):
                FILE_LIST.append(imageFileName.name)


    for i, imageName in enumerate(FILE_LIST):
        if ((numberOfIterations > 0) and (i > numberOfIterations)):
            break; # come of of the loop
        # Not allowed in python 2.7
        # print('.', end='', flush=True)
   
        bBirdFound, description, confidenceScore = DetectBirdInImage(outputFolder,imageName,confThreshold, imageTag )
        if (bBirdFound == True):
            TotalBirdsFound = TotalBirdsFound +1
            g_detectedImages.append({common._IMAGE_NAME_TAG:imageName, common._CONFIDENCE_SCORE_TAG:float('{0:.4f}'.format(confidenceScore))})
            if (verbosity == True):
                print("")
                print("Image name = {0}, imageTag = {1} , Confidence Score = {2:0.4f}, Description = {3}".format(imageName, imageTag, confidenceScore, description))


    elapsed_time = time.time() - start_time
    if (logResult == True):
        import datetime
        from  cosmosDB.cosmosDBWrapper import clsCosmosWrapper
        obj = clsCosmosWrapper()
        dictObject ={   common._IMAGE_DETECTION_PROVIDER_TAG : __name__,
                        common._EXPERIMENTNAME_TAG : experimentName,
                        common._DATETIME_TAG : str(datetime.datetime.now()),
                        common._ELAPSED_TIME_TAG : elapsed_time,
                        common._DETECTED_IMAGES_TAG : g_detectedImages,
                        'result - totalNumberOfRecords': len(FILE_LIST),
                        'result - birdFound' : TotalBirdsFound,
                        'param - confThreshold' : confThreshold, 
                        'param - numberOfIterations' : numberOfIterations,
                        'param - imageTag' : imageTag
                    }
        obj.logExperimentResult(documentDict= dictObject)

    return TotalBirdsFound 

if __name__ == "__main__":
    processImages()









