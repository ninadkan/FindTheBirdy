#OpenCVPhotoExtractorTest
import time
from openCVPhotoExtractor import processImages, _DESTINATIONFOLDER, g_verbosity
import platform 


ExportKeys = ['COSMOSDB_HOST', 'COSMOSDB_KEY', 'COSMOSDB_DATABASE', 'AZURE_VISION_API_KEY', 'GOOGLE_APPLICATION_CREDENTIALS']
# try to load it from the environmental variables

for keysToBeFound in ExportKeys:
    import os
    import sys
    _key = os.environ.get(keysToBeFound)
    if (_key is None ) or (len(_key) == 0):
        print("{0} Key not specified. Exiting".format(keysToBeFound))
        sys.exit(0)
          

BoundingRectList = [1000] #[2500, 2000, 1500, 1000]

osString = platform.platform()
NIX_DEFINED = True
if ('Windows' in osString):
    NIX_DEFINED = False


def delete_existing_files():
    import os

    if NIX_DEFINED:
        files = os.path.join(_DESTINATIONFOLDER,'*')
        cpCommand = "rm -r " +  files
    else:
        files = os.path.join(_DESTINATIONFOLDER,'*.*')
        cpCommand = "del /q " + files

    try:
        print(cpCommand)
        os.system(cpCommand)
    except Exception as e:
        print(e)
    return 

import time
import datetime
ExperimentName = "BirdImageDetection-" + str(datetime.datetime.now())
print(ExperimentName)
#ExperimentName ='BirdImageDetection-2018-11-03 02:32:04.704886'


for item in BoundingRectList:
        delete_existing_files()
        # premature end of JPEG was detected with 2018-04-22_0247. Remove that image 
        l, tt,  t = processImages(boundingRectAreaThreshold = item, logResult=True, experimentName=ExperimentName)
        print ("")
        print("Bounding Rectangle value = {0}".format(item))                
        print("Elapsed time = " + time.strftime("%H:%M:%S", time.gmtime(t))+ "Total images processed = {0}, detected = {1}".format(l, tt))
        #print ("True detection = {0:0.2f}, false +ve = {1:0.2f} , false negative = {2:0.2f}".format(tt, fp, fn))

from yoloBirdImageDetector import processImages as yoloTest, verbosity as yoloVerbosity
Detector = "Yolo Detector"
print(Detector)
yoloTest(experimentName=ExperimentName)

# Run the tests now
from mobileNetImageDetector import processImages as mobileTest
Detector = "Mobile Net Detector"
print(Detector)
mobileTest(experimentName=ExperimentName)

# Need to set environment variable AZURE_VISION_API_KEY
# Py36 environment
from azureImageDetector import processImages as azureTest, verbosity as azureVerbosity
Detector = "Azure Detector"
print(Detector)
azureTest(experimentName=ExperimentName)


#export GOOGLE_APPLICATION_CREDENTIALS=<path_to_service_account_file>
from googleImageDetector import processImages as googleTest, verbosity as googleVerbosity
Detector = "Google Detector"
print(Detector)
googleTest(experimentName=ExperimentName)


# Add our temporary reading of the images that we believe are the correct ones. These are not the 
# exhaustive list but atleast contain the superflous list. 
ExperimentName = 'BirdImageDetection-2018-11-09 14:09:51.541986'
_FILENAMEEXTENSION = '.jpg'
FILE_LIST = []
import os
for file in os.listdir(_DESTINATIONFOLDER):
    strFileName = file.replace(_FILENAMEEXTENSION,'')
    FILE_LIST.append(strFileName)
from  cosmosDB.cosmosDBWrapper import clsCosmosWrapper
clsObj = clsCosmosWrapper()
clsObj.savePhotoListToACollection(FILE_LIST, ExperimentName)


