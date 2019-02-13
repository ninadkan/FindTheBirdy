import numpy as np
import cv2
import os
import argparse
from pathlib import Path
import time
import common

import azureFS.azureFileShareTest as fs
import azureFS.mask_creation as mask


# Initialize DEFAULTS
_CONF_THRESHOLD = 0.5
_SHAPE_WEIGHT = 224

_YOLO_CONFIG_FOLDER = Path("./yolo/")

_CLASSESFILE  = os.path.join(_YOLO_CONFIG_FOLDER, "coco.names")
_MODELCONFIG = os.path.join(_YOLO_CONFIG_FOLDER, "yolov3.cfg")
_MODEL_WEIGHTS = os.path.join(_YOLO_CONFIG_FOLDER,"yolov3.weights")
_SCALE_FACTOR = 1/255
_NO_OF_ITERATIONS = -1 

_NMS_THRESHOLD = 0.4
_LOG_RESULT = True
_EXPERIMENTNAME = ''

# specify global objects 
g_classes = None
g_net = None
verbosity = False

g_detectedImages = []

def init(classesFile, modelConfiguration, modelWeights):
    global g_net
    global g_classes
    with open(classesFile, 'rt') as f:
        g_classes = f.read().rstrip('\n').split('\n')
    g_net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
    g_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    g_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)


# Get the names of the output layers
def getOutputsNames():
    # Get the names of all the layers in the network
    layersNames = g_net.getLayerNames()
    # Get the names of the output layers, i.e. the layers with unconnected outputs
    return [layersNames[i[0] - 1] for i in g_net.getUnconnectedOutLayers()]

# Remove the bounding boxes with low confidence using non-maxima suppression
def postprocess(imageName, imageFrame, outs, confThreshold, imageTag, nmsThreshold):
    global g_detectedImages
    bBirdFound = False
    frameHeight = imageFrame.shape[0]
    frameWidth = imageFrame.shape[1]

    # Scan through all the bounding boxes output from the network and keep only the
    # ones with high confidence scores. Assign the box's class label as the class with the highest score.
    classIds = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                center_x = int(detection[0] * frameWidth)
                center_y = int(detection[1] * frameHeight)
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])

    # Perform non maximum suppression to eliminate redundant overlapping boxes with
    # lower confidences.

    indices = cv2.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    for i in indices:
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]

        #DEBUG__
        # Get the label for the class name and its confidence
        if g_classes:
            assert(classId < len(g_classes))
            bird = '%s' % (g_classes[classIds[i]])
            if (bird == imageTag):
                bBirdFound = True
                g_detectedImages.append({ common._IMAGE_NAME_TAG:imageName, common._CONFIDENCE_SCORE_TAG:float('{0:.4f}'.format(confidences[i]))})
                if (verbosity == True):
                    print("")
                    print("Image name = {0}, Bird Found = {1}, Confidence Score = {2}".format(imageName, bBirdFound, confidences[i]))

                break; 
    return bBirdFound

def YoloBirdDetector(imageName, imageFrame, scaleFactor, shapeWeight, confThreshold, imageTag, nmsThreshold):
    bRV = False
    blob = cv2.dnn.blobFromImage(imageFrame, scaleFactor, (shapeWeight, shapeWeight), [0,0,0], 1, crop=False)

    # Sets the input to the network
    g_net.setInput(blob)
    # Runs the forward pass to get output of the output layers
    outs = g_net.forward(getOutputsNames())

    # Remove the bounding boxes with low confidence and give result
    if (postprocess(imageName,imageFrame, outs, confThreshold, imageTag, nmsThreshold) == True): 
        bRV = True
    
    return bRV
 
def processImages(  outputFolder = common._SRCIMAGEFOLDER,
                    confThreshold = _CONF_THRESHOLD, 
                    shapeWeight = _SHAPE_WEIGHT,
                    yoloConfigurationFolder = _YOLO_CONFIG_FOLDER, 
                    classesFile = _CLASSESFILE ,
                    modelConfiguration = _MODELCONFIG, 
                    modelWeights = _MODEL_WEIGHTS, 
                    scaleFactor = _SCALE_FACTOR , 
                    numberOfIterations = _NO_OF_ITERATIONS,
                    imageTag = common._IMAGE_TAG,
                    nmsThreshold = _NMS_THRESHOLD, 
                    logResult = _LOG_RESULT,
                    experimentName = _EXPERIMENTNAME,
                    messageId=None):
    '''
    Process the image and output if it has detected any birds in the images
    outputFolder IMAGE_SRC_FOLDER = Location of image files
    confThreshold CONF_THRESHOLD = Minimum confidence threshold
    shapeWeight SHAPE_WEIGHT = Shape weight to be used in DNN blobFromImage fn
    yoloConfigurationFolder YOLO_CONFIG_FOLDER = Yolo folder
    classesFile CLASSESFILE = Classes file location
    modelConfiguration MODELCONFIG = Configuration filename location
    modelWeights MODEL_WEIGHTS = Model weights filename location
    numberOfIterations NO_OF_ITERATIONS = Maximum number of images to be searched. set to <0 for all
    imageTag IMAGE_TAG = The tag to be searched for
    scaleFactor SCALE_FACTOR = Scale factor to be used in DNN blobFromImage
    nmsThreshold _NMS_THRESHOLD nmsThreshold used in the cv2.dnn.NMSBoxes fn
    '''
    global g_detectedImages
    g_detectedImages = []
    start_time = time.time()

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


    # initialize Yolo client 
    init(classesFile, modelConfiguration, modelWeights)
    
    TotalBirdsFound = 0

    for i, imageName in enumerate(FILE_LIST):
        if ((numberOfIterations > 0) and (i > numberOfIterations)):
            break; # come of of the loop
        print('.', end='', flush=True)

        imageFrame = None

        if (common._FileShare == False):
            pathToFileInDisk= os.path.join(outputFolder,imageName)
            imageFrame = cv2.imread(pathToFileInDisk)
        else:
            brv, desc, imageFrame = mask.GetRawImage(common._FileShareName, outputFolder, imageName)
            assert(brv == True), "Unable to load " + imageName

        assert(imageFrame is not None), "Unable to load " + imageName

        bBirdFound =  YoloBirdDetector(imageName, imageFrame, scaleFactor, shapeWeight, confThreshold, imageTag, nmsThreshold)
        if (bBirdFound == True):
            TotalBirdsFound = TotalBirdsFound +1

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
                        'param - shapeWeight' : shapeWeight,
                        'param - scaleFactor' : scaleFactor , 
                        'param - numberOfIterations' : numberOfIterations,
                        'param - imageTag' : imageTag,
                        'param - nmsThreshold' : nmsThreshold,
                        common._MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID:messageId
                    }
        obj.logExperimentResult(documentDict= dictObject)
    return TotalBirdsFound


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser = argparse.ArgumentParser(description=__doc__,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose", help="increase output verbosity",action="store_true")
    subparsers = parser.add_subparsers(dest="command")
    process_parser = subparsers.add_parser("processImages", help=processImages.__doc__)

    process_parser.add_argument("outputFolder", nargs='?', default=common._SRCIMAGEFOLDER, help="Location of image files")
    process_parser.add_argument("confThreshold", nargs='?', default=_CONF_THRESHOLD, help="Minimum confidence threshold")
    process_parser.add_argument("shapeWeight", nargs='?', default=_SHAPE_WEIGHT, help="Shape weight to be used in DNN blobFromImage fn")
    process_parser.add_argument("yoloConfigurationFolder", nargs='?', default=_YOLO_CONFIG_FOLDER, help="Yolo folder")
    process_parser.add_argument("classesFile", nargs='?', default=_CLASSESFILE, help="Classes file location")
    process_parser.add_argument("modelConfiguration", nargs='?', default=_MODELCONFIG, help="Configuration filename location")
    process_parser.add_argument("modelWeights", nargs='?', default=_MODEL_WEIGHTS, help="Model weights filename location")
    process_parser.add_argument("numberOfIterations", nargs='?', default=_NO_OF_ITERATIONS, help="Maximum number of images to be searched. set to <0 for all")
    process_parser.add_argument("imageTag", nargs='?', default=common._IMAGE_TAG, help="The tag to be searched for")
    process_parser.add_argument("scaleFactor", nargs='?', default=_SCALE_FACTOR, help="Scale factor to be used in DNN blobFromImage")
    process_parser.add_argument("nmsThreshold", nargs='?', default=_NMS_THRESHOLD, help="Used in the cv2.dnn.NMSBoxes fn")
    process_parser.add_argument("logResult", nargs='?', default=_LOG_RESULT, help="Log result to cosmos DB")
    process_parser.add_argument("experimentName", nargs='?', default=_EXPERIMENTNAME, help="Common name of collection under cosmos DB")

   
    args = parser.parse_args()
    if args.command == "processImages":
        if (args.verbose):
            verbosity = True

        import time
        Detector = "Yolo Detector"
        start_time = time.time()
        TotalBirdsFound  = processImages(   outputFolder = args.outputFolder,
                                            confThreshold = args.confThreshold,
                                            shapeWeight = args.shapeWeight,
                                            yoloConfigurationFolder = args.yoloConfigurationFolder,
                                            classesFile = args.classesFile,
                                            modelConfiguration = args.modelConfiguration,
                                            modelWeights = args.modelWeights,
                                            scaleFactor = args.scaleFactor,
                                            numberOfIterations = args.numberOfIterations,
                                            imageTag = args.imageTag,
                                            nmsThreshold = args.nmsThreshold,
                                            logResult=args.logResult,
                                            experimentName=args.experimentName)
        end_time = time.time() - start_time

        print("")
        print(Detector)                
        print("Total bird images found  = {0}".format(TotalBirdsFound) + "  " + "Elapsed time = " + time.strftime("%H:%M:%S", time.gmtime(end_time)))
        





