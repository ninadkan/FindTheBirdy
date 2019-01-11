#lets create the basic template
# sources
# https://www.programcreek.com/python/example/89404/cv2.createBackgroundSubtractorMOG2
# https://docs.opencv.org/3.3.0/db/d5c/tutorial_py_bg_subtraction.html
# 
import argparse
import numpy as np
import cv2
import os
import time
import json
import time


from pathlib import Path
import common
import docker_clsOpenCVProcessImages as ds
import azureFS.azureFileShareTest as fs


_LOGRESULT = True   # Should we write the results to CosmosDB or not. This is dependent on _WRITEOUTPUT values.
                    # as it looks at the files copied into destination folder
_MAX_NUM_OF_DOCKER_CONTAINERS = int(3)
_SLEEP_TIME_BEFFORE_CHECK = int(10) # # seems like a good value, remember its in seconds; me thinks 



# The source folder structure is: SourceShareFolder() + CommonFolder(='object-detection') + ExperimentName=('DD-MM-YYYY')
# The destination folder is source folder plus destination (='output')
# Depending on the protocol used to access the files, https or SMB, the base folder changes

class clsOpenCVObjectDetector:
    def __init__(self, experimentName):
        # Load passed parameters
        self.experimentName = experimentName
        # directory and folder parameters
        self.srcImageFolder = common._SRCIMAGEFOLDER        
        self.destinationFolder = common._DESTINATIONFOLDER
        # To log result or not
        self.logResult = _LOGRESULT
        return

    def get_logResult(self):
        return self.logResult 
    
    def set_logResult(self, value):
        self.logResult = value
        return     


    def processImages(self,imageBatchSize, partOfFileName=''):
        start_time = time.time()
        fileList = []
        TotalImageCount = 0
        if (common._FileShare == False):
            # Important, that the structure of images to be loaded is pre-defined. 
            # Now the srcImageFolder contains the final directory name. 
            self.srcImageFolder = os.path.join(self.srcImageFolder,self.experimentName)
            # update the location where our output is to be written back
            self.destinationFolder = os.path.join(self.srcImageFolder,self.destinationFolder)

            if not os.path.exists(self.destinationFolder):
                print("creating folder {0}".format(self.destinationFolder))
                os.makedirs(self.destinationFolder)

            # populate the file_list for this class
            
            for file in os.listdir(self.srcImageFolder):
                if os.path.isfile(os.path.join(self.srcImageFolder,file)) and file.endswith(common._FILENAMEEXTENSION):
                    if (len(partOfFileName) >0):
                        if (partOfFileName in file):
                            fileList.append(file)
                            TotalImageCount +=1
                    else:
                        fileList.append(file)
                        TotalImageCount +=1       
        else:
            self.srcImageFolder = self.srcImageFolder + "/" + self.experimentName
            self.destinationFolder = self.srcImageFolder + "/" + self.destinationFolder
            brv, desc, myROI  = fs.createDirectory(common._FileShareName, self.destinationFolder)
            assert(brv == True), "Unable to create/locate output directory " + destinationFolder

            brv, desc, lst = fs.getListOfAllFiles(common._FileShareName, self.srcImageFolder)
            if (brv == True):
                if (not(lst is None or len(lst)<1)):
                    for i, imageFileName in enumerate(lst):
                        if (imageFileName.name.endswith(common._FILENAMEEXTENSION)):
                            if (len(partOfFileName) >0):
                                if (partOfFileName in imageFileName.name):
                                    fileList.append(imageFileName.name)
                                    TotalImageCount +=1
                            else:
                                fileList.append(imageFileName.name)
                                TotalImageCount +=1
                else:
                    print("Directory is either None or zero order")
            else:
                print("fs.getListOfAllFiles returned False")

        
        if (len(fileList) > 0):
            # create chunks for the filelist That is created
            l = len(fileList)
            # Batch size of one would be used here
            if (common._UseDocker == False):
                for pos in range(0, l , l):
                    objProc = ds.clsOpenCVProcessImages()
                    objProc.set_verbosity(False)
                    objProc.processImages(  offset = pos, 
                                            imageSrcFolder = self.srcImageFolder,  
                                            imageDestinationFolder = self.destinationFolder, 
                                            experimentName = self.experimentName, 
                                            imageBatchSize = l, 
                                            partOfFileName=  partOfFileName)
            else:
                # use docker to manage the image processing, should I not be doing separate threading? 
                import docker
                client = docker.from_env()
                dictOfDockerContainerIds = dict()
                # the environment variable needs to be passed as following 
                # environment={'FOO': 'BAR'},
                # https://github.com/docker/docker-py/blob/master/tests/unit/models_containers_test.py

               
                imageBatchSize = int(l/_MAX_NUM_OF_DOCKER_CONTAINERS) # change it here to make the comparision betwenn the two options equal. 

                envString=dict()
                envString['EXPERIMENT_NAME']= str(self.experimentName)
                envString['BATCH_SIZE'] = int(imageBatchSize)
                
                for pos in range(0, l , imageBatchSize):
                    dockerImageName = "imagedetector:0.2"
                    envString['OFFSET'] = int(pos)
                    #print (envString)
                    container = client.containers.run(dockerImageName, detach=True, environment=envString)
                    #print(container.id)
                    # set dictionary flag indicating the Container has not exited as yet                    
                    dictOfDockerContainerIds[container.id] = False

                print("All containers are now running...")
                allContainersHaveExited = False

                while (allContainersHaveExited == False):
                    # print('Sleeping...')
                    time.sleep(_SLEEP_TIME_BEFFORE_CHECK) 
                    allContainersHaveExited = True
                    for key, value in dictOfDockerContainerIds.items():
                        if (value == False): # indicating that the container at last status check was still running
                            localContainer = client.containers.get(key)
                            if (localContainer is not None):
                                #print(localContainer.logs())
                                #print(key + " : " + str(value) +  " : " + localContainer.status)
                                if (localContainer.status == "exited"): #update the value
                                    dictOfDockerContainerIds[key] = True
                                else: 
                                    allContainersHaveExited = False
                            else:
                                # WTF
                                print("Container Missing ::" + key)
        else:
            assert (False), "Error Loading file list" 
        

        
        # Write the log thingy now
        detectedImages = []
        TotalNumberOfImagesDetected = 0

        if (common._FileShare == False):
            for file in os.listdir(self.destinationFolder):
                jsonObject = {common._IMAGE_NAME_TAG: file, common._CONFIDENCE_SCORE_TAG:1}
                detectedImages.append(jsonObject)
                TotalNumberOfImagesDetected +=1
        else:
            brv, desc, lst = fs.getListOfAllFiles(common._FileShareName, self.destinationFolder)
            if (brv == True):
                if (not(lst is None or len(lst)<1)):
                    for i, imageFileName in enumerate(lst):
                        TotalNumberOfImagesDetected +=1
                        jsonObject = {common._IMAGE_NAME_TAG: imageFileName.name, common._CONFIDENCE_SCORE_TAG:1}
                        detectedImages.append(jsonObject)
        
        elapsed_time = time.time() - start_time
        self.WriteLogsToDatabase(self.experimentName, elapsed_time, partOfFileName, detectedImages, TotalNumberOfImagesDetected, TotalImageCount)

        return len(fileList), 0,  elapsed_time




    def WriteLogsToDatabase(self, experimentName, elapsed_time, partOfFileName, detectedImages, TotalNumberOfImagesDetected, TotalImageCount):
        if (self.logResult == True):
            import datetime
            from  cosmosDB.cosmosDBWrapper import clsCosmosWrapper

            obj = clsCosmosWrapper()
            objProc = ds.clsOpenCVProcessImages()
            dictObject = {  common._IMAGE_DETECTION_PROVIDER_TAG : __name__,
                            common._EXPERIMENTNAME_TAG : experimentName,
                            common._DATETIME_TAG : str(datetime.datetime.now()),
                            common._ELAPSED_TIME_TAG : elapsed_time,
                            common._DETECTED_IMAGES_TAG : detectedImages,
                            'result-totalNumberOfRecords': TotalImageCount,
                            'TotalNumberOfImagesDetected' : TotalNumberOfImagesDetected,
                            'param-numImagesToCreateMeanBackground' : objProc.get_numImagesToCreateMeanBackground(), 
                            'param-grayImageThreshold' : objProc.get_grayImageThreshold(), 
                            'param-numberOfImagesToProcess' : -1, 
                            'param-boundingRectAreaThreshold' : objProc.get_boundingRectAreaThreshold(), 
                            'param-contourCountThreshold' : objProc.get_contourCountThreshold(),
                            'param-maskDiffThreshold' : objProc.get_maskDiffThreshold(),
                            'param-partOfFileName' : partOfFileName
                            }
            obj.logExperimentResult(documentDict= dictObject)





