# import the necessary packages
import numpy as np
import argparse
import cv2
import os
from pathlib import Path
import time

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
_CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]

_MOBILE_NET_FOLDER = Path("./mobileNet/")
_OUTPUT_FOLDER = Path('../data/outputopencv/')
_PROTOTXT = os.path.join(_MOBILE_NET_FOLDER, 'MobileNetSSD_deploy.prototxt.txt')
_MODEL = os.path.join(_MOBILE_NET_FOLDER,'MobileNetSSD_deploy.caffemodel')
#common DEFAULTS
_CONF_THRESHOLD = 0.5
_SHAPE_WEIGHT = 224
_SCALE_FACTOR = 1/255
_NO_OF_ITERATIONS = -1 
_IMAGE_TAG = "bird"
_LOG_RESULT = True
_EXPERIMENTNAME = ''


#Global Variable
g_net = None
verbosity = True
detectedImages = []

# load our serialized _MODEL from disk
def init(prototxt, model):
    global g_net
    g_net = cv2.dnn.readNetFromCaffe(prototxt, model)
    return 

# load the input image and construct an input blob for the image
# by resizing to a fixed 300x300 pixels and then normalizing it
# (note: normalization is done via the authors of the MobileNet SSD
# implementation)

def MobileNetBirdDetector(imageName, imageFrame, scaleFactor, shapeWeight, confThreshold, imageTag):
    global detectedImages 
    bRV = False
 
    blob = cv2.dnn.blobFromImage(imageFrame, scaleFactor, (shapeWeight, shapeWeight), [0,0,0], 1, crop=False)
    g_net.setInput(blob)
    detections = g_net.forward()

    # loop over the detections
    for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with the
        # prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence > confThreshold:
            # extract the index of the class label from the `detections`,
            # then compute the (x, y)-coordinates of the bounding box for
            # the object
            idx = int(detections[0, 0, i, 1])
            if (_CLASSES[idx] == imageTag):
                bRV = True
                detectedImages.append({'ImageName':imageName, 'ConfidenceSore':float('{0:.4f}'.format(confidence))})
                if (verbosity == True):
                    print("")
                    print("Image name = {0}, imageTag = {1} , Confidence Score = {2}".format(imageName, imageTag, confidence))
                break
    return bRV

def processImages(  outputFolder = _OUTPUT_FOLDER,
                    confThreshold = _CONF_THRESHOLD, 
                    shapeWeight = _SHAPE_WEIGHT,
                    scaleFactor = _SCALE_FACTOR , 
                    mobileNetFolder = _MOBILE_NET_FOLDER, 
                    model = _MODEL, 
                    prototxt = _PROTOTXT, 
                    numberOfIterations = _NO_OF_ITERATIONS,
                    imageTag = _IMAGE_TAG,
                    logResult = _LOG_RESULT,
                    experimentName = _EXPERIMENTNAME):
    
    '''
    Process the image and output if it has detected any birds in the images
    outputFolder IMAGE_SRC_FOLDER = Location of image files
    confThreshold CONF_THRESHOLD = Minimum confidence threshold
    shapeWeight SHAPE_WEIGHT = Shape weight to be used in DNN blobFromImage fn
    scaleFactor SCALE_FACTOR = Scale factor to be used in DNN blobFromImage
    mobileNetFolder = _MOBILE_NET_FOLDER, folder location where mobile net files are stored
    model = _MODEL, filename and location where model file is stored
    prototxt = _PROTOTXT; filename and location where prototxt file is stored
    numberOfIterations NO_OF_ITERATIONS = Maximum number of images to be searched. set to <0 for all
    imageTag IMAGE_TAG = The tag to be searched for, default = "bird"
    '''
    start_time = time.time()
    FILE_LIST = []
    for file in os.listdir(outputFolder):
        FILE_LIST.append(file)
    # initialize Yolo client 
    init(prototxt, model)
    
    TotalBirdsFound = 0

    for i, imageName in enumerate(FILE_LIST):
        if ((numberOfIterations > 0) and (i > numberOfIterations)):
            break; # come of of the loop
        print('.', end='', flush=True)
        pathToFileInDisk= os.path.join(outputFolder,imageName)
        imageFrame = cv2.imread(pathToFileInDisk)
        assert(imageFrame is not None), "Unable to load " + pathToFileInDisk

        bBirdFound =  MobileNetBirdDetector(imageName, imageFrame, scaleFactor, shapeWeight, confThreshold, imageTag)
        if (bBirdFound == True):
            TotalBirdsFound = TotalBirdsFound +1

    elapsed_time = time.time() - start_time

    if (logResult == True):
        import datetime
        from  cosmosDB.cosmosDBWrapper import clsCosmosWrapper
        obj = clsCosmosWrapper()
        dictObject ={  'id': __name__,
                        'DateTime': str(datetime.datetime.now()),
                        'elapsedTime': elapsed_time,
                        'result - totalNumberOfRecords': len(FILE_LIST),
                        'result - birdFound' : TotalBirdsFound,
                        'param - confThreshold' : confThreshold, 
                        'param - shapeWeight' : shapeWeight,
                        'param - scaleFactor' : scaleFactor , 
                        'param - numberOfIterations' : numberOfIterations,
                        'param - imageTag' : imageTag,
                        'detectedItems': detectedImages
                    }
        obj.logExperimentResult(collectionName = experimentName, documentDict= dictObject)
    return TotalBirdsFound                    


if __name__ == "__main__":
    processImages()
