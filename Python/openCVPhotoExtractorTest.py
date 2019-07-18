#OpenCVPhotoExtractorTest
import time
from common import _SRCIMAGEFOLDER, _DESTINATIONFOLDER, _FileShare, _FileShareName
import openCVPhotoExtractorClsImpl
#import azureFS.azureFileShareTest as fs
import storageFileService as sf
import platform
import os

globalStorageSrv = sf.storageFileService(None)

import logging
from loggingBase import getGlobalHandler, getGlobalLogObject, clsLoggingBase
g_logObj = getGlobalLogObject(__name__)

def delete_existing_files(experimentName):
    global globalStorageSrv
    global g_logObj
    brv = False
    if (_FileShare == False):
        
        files = os.path.join(_SRCIMAGEFOLDER,experimentName)
        files = os.path.join(files, _DESTINATIONFOLDER)

        osString = platform.platform()

        
        UNIX_DEFINED = True
        if sys.platform == 'win32':  # pragma: no cover
        #if ('Windows' in osString):
            UNIX_DEFINED = False

        if UNIX_DEFINED:
            files = os.path.join(files,'*')
            g_logObj.info(files)
            cpCommand = "rm -r " +  files
        else:
            files = os.path.join(files,'*.*')
            g_logObj.info(files)
            cpCommand = "del /q " + files

        try:
            g_logObj.info(cpCommand)
            os.system(cpCommand)
            brv = True
        except Exception as e:
            g_logObj.error(e)
        return
    else:
        # cloudy environment
        srcImageFolder = _SRCIMAGEFOLDER + "/" + experimentName
        destinationFolder = srcImageFolder + "/" + _DESTINATIONFOLDER
        g_logObj.info(destinationFolder)
        brv, desc, ret  = globalStorageSrv.removeAllFiles(_FileShareName, destinationFolder)
        if(brv == False):
            g_logObj.error( "Unable to create/locate output directory " + destinationFolder)
            return brv
    return brv

def checkExportKeysSetup():
    global g_logObj
    # check that the environment contains all the right variables defined
    brv = True
    ExportKeys = ['COSMOSDB_HOST', 'COSMOSDB_KEY', 'COSMOSDB_DATABASE', 'AZURE_VISION_API_KEY', 'GOOGLE_APPLICATION_CREDENTIALS']
    # try to load it from the environmental variables
    for keysToBeFound in ExportKeys:
        import os
        import sys
        _key = os.environ.get(keysToBeFound)
        if (_key is None ) or (len(_key) == 0):
            g_logObj.error("{0} Export Key not specified. Exiting".format(keysToBeFound))
            brv = False
            #sys.exit(0) # let someone else decide if they want to exit 
    return brv

def runExperiments(ExperimentNames = None, startIndex = 0,NumberOfExperimentsToProcess = -1):
    global globalStorageSrv
    global g_logObj
# ExperimentName contains the list of experiments that need to be started. 
# what is our starting offset
# startIndex = 27
# How many experiments are we be processing. Start with 1, which executes for two experiments and then set to -1 for the complete list. 
# NumberOfExperimentsToProcess = 25
# Get all the names of the experiments. 
# ExperimentNames = None

    if (ExperimentNames == None):   # if nothing is passed, then update accordingly
        NumberOfExperimentsToProcess = 1 # we will not process everything if nothing is specified
        if (_FileShare == False):
            ExperimentNames = os.listdir(_SRCIMAGEFOLDER)
        else:
            rv, elapsedTime, ExperimentNames = globalStorageSrv.TestGetAllExperimentNames(_FileShareName, _SRCIMAGEFOLDER)

    # Lets start our test. 
    if (ExperimentNames is not None and len(ExperimentNames) > 0):
        for i, ExperimentName in enumerate(ExperimentNames):
            if (i >= startIndex ):
                if ((NumberOfExperimentsToProcess > 0) and (i > NumberOfExperimentsToProcess+startIndex)):
                    break; # come of of the loop, we've iterated enough

                g_logObj.info(ExperimentName.name)
                BoundingRectList = [1000] #[2500, 2000, 1500, 1000]
                for item in BoundingRectList:
                        delete_existing_files(ExperimentName.name)
                        # premature end of JPEG was detected with 2018-04-22_0247. Remove that image 
                        procObject = openCVPhotoExtractorClsImpl.clsOpenCVObjectDetector(experimentName=ExperimentName.name)
                        #l, tt,  t = procObject.processImages(partOfFileName='2018-12-14_04')
                        l, tt,  t = procObject.processImages()
                        g_logObj.info ("")
                        g_logObj.info("Bounding Rectangle value = {0}".format(item))                
                        g_logObj.info("Elapsed time = " + time.strftime("%H:%M:%S", time.gmtime(t))+ "Total images processed = {0}, detected = {1}".format(l, tt))
                        #g_logObj.info ("True detection = {0:0.2f}, false +ve = {1:0.2f} , false negative = {2:0.2f}".format(tt, fp, fn))

                from yoloBirdImageDetector import processImages as yoloTest
                Detector = "Yolo Detector"
                g_logObj.info(Detector)
                yoloTest(experimentName=ExperimentName.name)

                # Run the tests now
                from mobileNetImageDetector import processImages as mobileTest
                Detector = "Mobile Net Detector"
                g_logObj.info(Detector)
                mobileTest(experimentName=ExperimentName.name)

                # Need to set environment variable AZURE_VISION_API_KEY
                # Py36 environment
                # from azureImageDetector import processImages as azureTest, verbosity as azureVerbosity
                # Detector = "Azure Detector"
                # g_logObj.info(Detector)
                # azureTest(experimentName=ExperimentName.name)


                #export GOOGLE_APPLICATION_CREDENTIALS=<path_to_service_account_file>
                from googleImageDetector import processImages as googleTest
                Detector = "Google Detector"
                g_logObj.info(Detector)
                googleTest(experimentName=ExperimentName.name)



def runAll(experimentName = None):
    if (checkExportKeysSetup() == True):
        if (delete_existing_files(experimentName) == True) :
            runExperiments(ExperimentNames)

if __name__ == "__main__":
    runAll()

