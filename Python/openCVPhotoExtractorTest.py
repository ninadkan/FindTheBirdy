#OpenCVPhotoExtractorTest
import time
from common import _SRCIMAGEFOLDER, _DESTINATIONFOLDER, _FileShare, _FileShareName
import openCVPhotoExtractorClsImpl
import azureFS.azureFileShareTest as fs
import platform



osString = platform.platform()
NIX_DEFINED = True
if ('Windows' in osString):
    NIX_DEFINED = False


def delete_existing_files(experimentName):
    if (_FileShare == False):
        import os
        files = os.path.join(_SRCIMAGEFOLDER,experimentName)
        files = os.path.join(files, _DESTINATIONFOLDER)
        if NIX_DEFINED:
            files = os.path.join(files,'*')
            print(files)
            cpCommand = "rm -r " +  files
        else:
            files = os.path.join(files,'*.*')
            print(files)
            cpCommand = "del /q " + files

        try:
            print(cpCommand)
            os.system(cpCommand)
        except Exception as e:
            print(e)
        return
    else:
        srcImageFolder = _SRCIMAGEFOLDER + "/" + experimentName
        destinationFolder = srcImageFolder + "/" + _DESTINATIONFOLDER
        print(destinationFolder)
        brv, desc, ret  = fs.removeAllFiles(_FileShareName, destinationFolder)
        assert(brv == True), "Unable to create/locate output directory " + destinationFolder

# check that the environment contains all the right variables defined
ExportKeys = ['COSMOSDB_HOST', 'COSMOSDB_KEY', 'COSMOSDB_DATABASE', 'AZURE_VISION_API_KEY', 'GOOGLE_APPLICATION_CREDENTIALS']
# try to load it from the environmental variables
for keysToBeFound in ExportKeys:
    import os
    import sys
    _key = os.environ.get(keysToBeFound)
    if (_key is None ) or (len(_key) == 0):
        print("{0} Key not specified. Exiting".format(keysToBeFound))
        sys.exit(0)


# what is our starting offset
startIndex = 27
# How many experiments are we be processing. Start with 1, which executes for two experiments and then set to -1 for the complete list. 
NumberOfExperimentsToProcess = 25
# Get all the names of the experiments. 
ExperimentNames = None

if (_FileShare == False):
    ExperimentNames = os.listdir(_SRCIMAGEFOLDER)
else:
    rv, elapsedTime, ExperimentNames = fs.TestGetAllExperimentNames(_FileShareName, _SRCIMAGEFOLDER)

# Lets start our test. 
if (ExperimentNames is not None and len(ExperimentNames) > 0):
    for i, ExperimentName in enumerate(ExperimentNames):
        if (i >= startIndex ):
            if ((NumberOfExperimentsToProcess > 0) and (i > NumberOfExperimentsToProcess+startIndex)):
                break; # come of of the loop, we've iterated enough

            print(ExperimentName.name)
            BoundingRectList = [1000] #[2500, 2000, 1500, 1000]

            for item in BoundingRectList:
                    delete_existing_files(ExperimentName.name)
                    # premature end of JPEG was detected with 2018-04-22_0247. Remove that image 
                    procObject = openCVPhotoExtractorClsImpl.clsOpenCVObjectDetector(experimentName=ExperimentName.name)
                    #l, tt,  t = procObject.processImages(imageBatchSize=25, partOfFileName='2018-12-14_04')
                    l, tt,  t = procObject.processImages(imageBatchSize=25)
                    print ("")
                    print("Bounding Rectangle value = {0}".format(item))                
                    print("Elapsed time = " + time.strftime("%H:%M:%S", time.gmtime(t))+ "Total images processed = {0}, detected = {1}".format(l, tt))
                    #print ("True detection = {0:0.2f}, false +ve = {1:0.2f} , false negative = {2:0.2f}".format(tt, fp, fn))

            from yoloBirdImageDetector import processImages as yoloTest, verbosity as yoloVerbosity
            Detector = "Yolo Detector"
            print(Detector)
            yoloTest(experimentName=ExperimentName.name)

            # Run the tests now
            from mobileNetImageDetector import processImages as mobileTest
            Detector = "Mobile Net Detector"
            print(Detector)
            mobileTest(experimentName=ExperimentName.name)

            # Need to set environment variable AZURE_VISION_API_KEY
            # Py36 environment
            # from azureImageDetector import processImages as azureTest, verbosity as azureVerbosity
            # Detector = "Azure Detector"
            # print(Detector)
            # azureTest(experimentName=ExperimentName.name)


            #export GOOGLE_APPLICATION_CREDENTIALS=<path_to_service_account_file>
            from googleImageDetector import processImages as googleTest, verbosity as googleVerbosity
            Detector = "Google Detector"
            print(Detector)
            googleTest(experimentName=ExperimentName.name)


    # Add our temporary reading of the images that we believe are the correct ones. These are not the 
    # exhaustive list but atleast contain the superflous list. 
    # ExperimentName = 'BirdImageDetection-2018-11-09 14:09:51.541986'
    # _FILENAMEEXTENSION = '.jpg'
    # FILE_LIST = []
    # import os
    # for file in os.listdir(_DESTINATIONFOLDER):
    #     strFileName = file.replace(_FILENAMEEXTENSION,'')
    #     FILE_LIST.append(strFileName)
    # from  cosmosDB.cosmosDBWrapper import clsCosmosWrapper
    # clsObj = clsCosmosWrapper()
    # clsObj.savePhotoListToACollection(FILE_LIST, ExperimentName)


