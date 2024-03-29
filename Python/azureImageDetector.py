import time 
import requests
import cv2
import os
import sys
from pathlib import Path

import common
# import azureFS.azureFileShareTest as fs
# import azureFS.mask_creation as mask

import storageFileService as sf
globalStorageSrv = sf.storageFileService(None)

import logging
from loggingBase import getGlobalHandler, getGlobalLogObject, clsLoggingBase
g_logObj = getGlobalLogObject(__name__)



# https://github.com/Microsoft/Cognitive-Vision-Python/blob/master/Jupyter%20Notebook/Computer%20Vision%20API%20Example.ipynb 
# https://anaconda.org/conda-forge/requests

# Variables
_region = 'westeurope' #Here you enter the region of your subscription
#analyze
#_url = 'https://{}.api.cognitive.microsoft.com/vision/v1.0/analyze'.format(_region)
#tag
_url = 'https://{}.api.cognitive.microsoft.com/vision/v2.0/tag'.format(_region)
_maxNumRetries = 10
_CONF_THRESHOLD = 0.5
_NO_OF_ITERATIONS = -1


verbosity = False
_LOG_RESULT = True
_EXPERIMENTNAME = ''
g_detectedImages = []


def processRequest( json, data, headers, params ):
    """
    Helper function to process the request to Project Oxford
    Parameters:
    json: Used when processing images from its URL. See API Documentation
    data: Used when processing image read from disk. See API Documentation
    headers: Used to pass the key information and the data type request
    """
    global globalStorageSrv
    global g_logObj
    retries = 0
    result = None
    while True:
        response = requests.request( 'post', _url, json = json, data = data, headers = headers, params = params )
        if response.status_code == 429: 
            g_logObj.info( "Message: %s" % ( response.json() ) )
            if retries <= _maxNumRetries: 
                time.sleep(1) 
                retries += 1
                continue
            else: 
                g_logObj.warn( 'Error: failed after retrying!' )
                break
        elif response.status_code == 200 or response.status_code == 201:
            if 'content-length' in response.headers and int(response.headers['content-length']) == 0: 
                result = None 
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str): 
                if 'application/json' in response.headers['content-type'].lower(): 
                    result = response.json() if response.content else None 
                elif 'image' in response.headers['content-type'].lower(): 
                    result = response.content
        else:
            g_logObj.error( "Error code: %d" % ( response.status_code ) )
            g_logObj.error( "Message: %s" % ( response.json() ) )
        break
    return result

#DO NOT USE DIRECTLY... WILL BE REMOVED
def processImages(  _key = '', 
                    outputFolder = common._SRCIMAGEFOLDER,
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
    global g_logObj
    g_detectedImages = []
    start_time = time.time() 
    if (len(_key)== 0):
        # try to load it from the environmental variables
        _key = os.environ.get('AZURE_VISION_API_KEY')
        if (_key is None ) or (len(_key) == 0):
            print("Azure Vision API Key not specified. Exiting")
            sys.exit(0)
          

    FILE_LIST = []
    if (common._FileShare == False):
        outputFolder = os.path.join(outputFolder,experimentName)
        outputFolder = os.path.join(outputFolder,common._DESTINATIONFOLDER)
        for file in os.listdir(outputFolder):
            FILE_LIST.append(file)
    else:
        outputFolder = outputFolder + "/" + experimentName
        outputFolder = outputFolder + "/" + common._DESTINATIONFOLDER

        brv, desc, lst = globalStorageSrv.getListOfAllFiles(common._FileShareName, outputFolder)
        if (brv == True):
            for i, imageFileName in enumerate(lst):
                FILE_LIST.append(imageFileName.name)
    
    TotalBirdsFound = 0
    TotalHintBirdScore = 0

    for i, imageName in enumerate(FILE_LIST):
        if ((numberOfIterations > 0) and (i > numberOfIterations)):
            break; # come of of the loop
        #print('.', end='', flush=True)

        data = None
        if (common._FileShare == False):
            pathToFileInDisk= os.path.join(outputFolder,imageName)
            with open( pathToFileInDisk, 'rb' ) as f:
                data = f.read()
        else:
            brv, desc, data = globalStorageSrv.GetRawImageAsBytes(common._FileShareName, outputFolder, imageName)
            if (brv != True)
                g_logObj.error( "Error Get Raw Image" + imageName)
            return

            
        # Computer Vision parameters
        #analyze
        #params = { 'visualFeatures' : 'Color,Categories'} 
        #tag
        params ={}
        # For analyze, following is the complete list  
        # params = { 'visualFeatures' : 'Color,Categories, Tags, Description. Faces,ImageType,Adult'} 
        # if you want to add the language, details also as the key word, you'd construct is as follows
        # params = { 'visualFeatures' : 'Color,Categories', 'details': 'Celebrities, Landmarks', 'language':'en, ja,pt, zh'} 

        headers = dict()
        headers['Ocp-Apim-Subscription-Key'] = _key
        headers['Content-Type'] = 'application/octet-stream'

        json = None

        result = processRequest( json, data, headers, params )
        
        bBirdFound = False

        if result is not None:
            confidence = 0
            hintName = "Nothing"
            if ('tags' in result):
                sortedList = sorted(result['tags'], key=lambda x: x['confidence'], reverse=True)
                if (len(sortedList) > 0):
                    for item in sortedList: 
                        if('confidence' in item is None):
                            g_logObj.error("Confidence column missing")
                            return
                        if ('name' in item is None) :
                            g_logObj.error ("Name column missing")
                            return
                        confidence = item['confidence']
                        if (confidence > confThreshold):
                            tagName = item['name']
                            if (tagName == imageTag):
                                bBirdFound = True
                                TotalBirdsFound = TotalBirdsFound +1
                                g_detectedImages.append({common._IMAGE_NAME_TAG:imageName, common._CONFIDENCE_SCORE_TAG:float('{0:.4f}'.format(confidence))})
                                if (verbosity == True):
                                    #print("")
                                    g_logObj.info("Image name = {0}, imageTag = {1} , Confidence Score = {2}".format(imageName, imageTag, confidence))
                                break
                            else:
                                if ('hint' in item): # see if they think its available as a hint. 
                                    hintName = item['hint']
                                    if (hintName == imageTag):
                                        bBirdFound = True
                                        TotalBirdsFound = TotalBirdsFound +1
                                        TotalHintBirdScore = TotalHintBirdScore +1
                                        g_detectedImages.append({ common._IMAGE_NAME_TAG:imageName, common._CONFIDENCE_SCORE_TAG:float('{0:.4f}'.format(confidence)), 'Hint': TotalHintBirdScore})
                                        if (verbosity == True):
                                            #print("")
                                            g_logObj.info("Image name = {0}, imageTag = {1} , Confidence Score = {2} - Hint Option".format(imageName, imageTag, confidence))
                                        break

    elapsed_time = time.time() - start_time
    if (logResult == True):
        import datetime
        from  cosmosDBWrapper import clsCosmosWrapper
        obj = clsCosmosWrapper()
        dictObject ={   common._IMAGE_DETECTION_PROVIDER_TAG : __name__,
                        common._EXPERIMENTNAME_TAG : experimentName,
                        common._DATETIME_TAG : str(datetime.datetime.now()),
                        common._ELAPSED_TIME_TAG : elapsed_time,
                        common._DETECTED_IMAGES_TAG: g_detectedImages,
                        'result - totalNumberOfRecords': len(FILE_LIST),
                        'result - birdFound' : TotalBirdsFound,
                        'result - Hint bird Found' : TotalHintBirdScore, 
                        'param - confThreshold' : confThreshold, 
                        'param - numberOfIterations' : numberOfIterations,
                        'param - imageTag' : imageTag
                    }
        obj.logExperimentResult(documentDict= dictObject, removeExisting=False)
    
    return TotalBirdsFound

if __name__ == "__main__":
    processImages(experimentName='2018-04-15')







