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
import storageFileService as sf
#import azureFS.azureFileShareTest as fs

import eventMessageSender
import asyncio
#import cosmosDB.cosmosStatusUpdate
import cosmosStatusUpdate as cf


_LOGRESULT = True   # Should we write the results to CosmosDB or not. This is dependent on _WRITEOUTPUT values.
                    # as it looks at the files copied into destination folder
_MAX_NUM_OF_DOCKER_CONTAINERS = int(3)
_SLEEP_TIME_BEFFORE_CHECK = int(10) # # seems like a good value, remember its in seconds me thinks 

import logging
from loggingBase import clsLoggingBase

# The source folder structure is: SourceShareFolder() + CommonFolder(='object-detection') + ExperimentName=('DD-MM-YYYY')
# The destination folder is source folder plus destination (='output')
# Depending on the protocol used to access the files, https or SMB, the base folder changes

class clsOpenCVObjectDetector(clsLoggingBase):
    def __init__(self, experimentName):
        super().__init__(__name__)
        # Load passed parameters
        self.experimentName = experimentName
        # directory and folder parameters
        self.srcImageFolder = common._SRCIMAGEFOLDER        
        self.destinationFolder = common._DESTINATIONFOLDER
        # To log result or not
        self.logResult = _LOGRESULT
        self.MessageId = None
        #Storage and cosmos Object
        self.storageSrv = sf.storageFileService(None)
        self.cosmosStatusObj = cf.clsStatusUpdate()
        return

    def get_logResult(self):
        return self.logResult 
    
    def set_logResult(self, value):
        self.logResult = value
        return

    def get_MessageId(self):
        return self.MessageId

    def set_MessageId(self, value):
        self.MessageId = value
        return

    def getOnPremFileListAndCount(self, partOfFileName=''):
        fileListLocal = []
        TotalImageCountLocal = 0

        # Important, that the structure of images to be loaded is pre-defined. 
        # Now the srcImageFolder contains the final directory name. 
        self.srcImageFolder = os.path.join(self.srcImageFolder,self.experimentName)
        # update the location where our output is to be written back
        self.destinationFolder = os.path.join(self.srcImageFolder,self.destinationFolder)

        if not os.path.exists(self.destinationFolder):
            super().getLoggingObj().info("creating folder {0}".format(self.destinationFolder))
            os.makedirs(self.destinationFolder)

        # populate the file_list for this class
        
        for file in os.listdir(self.srcImageFolder):
            if os.path.isfile(os.path.join(self.srcImageFolder,file)) and file.endswith(common._FILENAMEEXTENSION):
                if (len(partOfFileName) >0):
                    if (partOfFileName in file):
                        fileListLocal.append(file)
                        TotalImageCountLocal +=1
                else:
                    fileListLocal.append(file)
                    TotalImageCountLocal +=1
        return fileListLocal, TotalImageCountLocal

    def getCloudFileListAndCount(self, partOfFileName=''): 
        fileListLocal = []
        TotalImageCountLocal = 0
        self.srcImageFolder = self.srcImageFolder + "/" + self.experimentName
        self.destinationFolder = self.srcImageFolder + "/" + self.destinationFolder
        super().getLoggingObj().info(common._FileShareName)
        super().getLoggingObj().info(self.destinationFolder)
        brv, desc, myROI  = self.storageSrv.createDirectory(common._FileShareName, self.destinationFolder)
        if(brv == False):
            super().getLoggingObj().error( "Unable to create/locate output directory " + self.destinationFolder)
            return None, None

        brv, desc, lst = self.storageSrv.getListOfAllFiles(common._FileShareName, self.srcImageFolder)
        if (brv == True):
            if (not(lst is None or len(lst)<1)):
                for i, imageFileName in enumerate(lst):
                    if (imageFileName.name.endswith(common._FILENAMEEXTENSION)):
                        if (len(partOfFileName) >0):
                            if (partOfFileName in imageFileName.name):
                                fileListLocal.append(imageFileName.name)
                                TotalImageCountLocal +=1
                        else:
                            fileListLocal.append(imageFileName.name)
                            TotalImageCountLocal +=1
            else:
                super().getLoggingObj().warn("Directory is either None or zero order")
                return None, None
        else:
            super().getLoggingObj().error("self.storageSrv.getListOfAllFiles returned False")
            return None, None
        return fileListLocal, TotalImageCountLocal

    async def processImages(self,partOfFileName=''):
        start_time = time.time()
        fileList = []
        TotalImageCount = 0
        if (common._FileShare == False):
            fileList, TotalImageCount = self.getOnPremFileListAndCount(partOfFileName)
        else:
            fileList, TotalImageCount = self.getCloudFileListAndCount(partOfFileName)
        
        if (len(fileList) > 0):
            # create chunks for the filelist That is created
            l = len(fileList)
            if (common._UseDocker == False and common._UseEventHub == False): # fallback to traditional mechanism
                for pos in range(0, l , l): # Batch size of one would be used here
                    objProc = ds.clsOpenCVProcessImages()
                    objProc.set_verbosity(False)
                    objProc.processImages(  offset = pos, 
                                            imageSrcFolder = self.srcImageFolder,  
                                            imageDestinationFolder = self.destinationFolder, 
                                            experimentName = self.experimentName, 
                                            imageBatchSize = l, 
                                            partOfFileName=  partOfFileName)
            elif (common._UseEventHub == True):
                # ideally store the message that you've got here and that you've started processing.
                # send the eventmessages to 
                # The number of Docker containers should be equal to number of EventHub Partitions
                imageBatchSize = 45 # int(l/(common._NUMBER_OF_EVENT_HUB_PARTITIONS*2))
                numberOfMessagesSent = 0
                for pos in range(0, l , imageBatchSize):
                    await eventMessageSender.sendProcessExperimentMessage(  self.get_MessageId(), 
                                                                            self.experimentName, 
                                                                            self.srcImageFolder,
                                                                            self.destinationFolder,
                                                                            imageBatchSize, 
                                                                            pos,
                                                                            partOfFileName)
                    numberOfMessagesSent += 1
                super().getLoggingObj().info("All messages ={} have now been send; waiting ..".format(numberOfMessagesSent))
                allMessagesProcessed = False
                wait_time = 60* 7 # six minutes from now
                stay_alive_time = 60*3 # 3 minutes wait time before sending a dummy message
                timeout = time.time() + wait_time
                next_stay_alive_time = time.time() + stay_alive_time
               
                while (allMessagesProcessed == False and time.time() < timeout):
                    # super().getLoggingObj().info('Sleeping...')
                    await asyncio.sleep(_SLEEP_TIME_BEFFORE_CHECK) 
                    #time.sleep(_SLEEP_TIME_BEFFORE_CHECK)
                    super().getLoggingObj().info("status check ...")
                    allMessagesProcessed = self.cosmosStatusObj.is_operationCompleted(self.get_MessageId(), self.experimentName, numberOfMessagesSent)
                    #super().getLoggingObj().info("... wait loop over status = {}".format(allMessagesProcessed))
                    if (allMessagesProcessed):
                        await eventMessageSender.sendDetectorMessages(  self.get_MessageId(), 
                                                                        self.experimentName, 
                                                                        self.destinationFolder)
                    else:
                        if (time.time() > next_stay_alive_time):
                            # send a stay alive message - this might interfere with auto kill feature of the 
                            super().getLoggingObj().info("Sending Stay Alive message ...")
                            await eventMessageSender.sendDetectorMessages(  self.get_MessageId(), 
                                                                            None, 
                                                                            None)
                            next_stay_alive_time = time.time() + stay_alive_time

                if (allMessagesProcessed is False):
                    super().getLoggingObj().info("Time out error triggered ...")
                    #log timeout error!
                    dictObject =    {  
                                        common._OPERATIONS_STATUS_MESSAGE_ID : self.get_MessageId(),
                                        common._OPERATIONS_STATUS_EXPERIMENT_NAME :self.experimentName,
                                        common._OPERATIONS_STATUS_OFFSET :0,
                                        common._OPERATIONS_STATUS_ELAPSED_TIME : '{}'.format(str(wait_time)),
                                        common._OPERATIONS_STATUS_STATUS_MESSAGE :"TIME OUT ERROR"
                                    }                    
                    self.cosmosStatusObj.insert_document_from_dict(dictObject, removeExisting=False)
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
                    #super().getLoggingObj().info (envString)
                    container = client.containers.run(dockerImageName, detach=True, environment=envString)
                    #super().getLoggingObj().info(container.id)
                    # set dictionary flag indicating the Container has not exited as yet                    
                    dictOfDockerContainerIds[container.id] = False

                super().getLoggingObj().info("All containers are now running...")
                allContainersHaveExited = False

                while (allContainersHaveExited == False):
                    # super().getLoggingObj().info('Sleeping...')
                    time.sleep(_SLEEP_TIME_BEFFORE_CHECK) 
                    allContainersHaveExited = True
                    for key, value in dictOfDockerContainerIds.items():
                        if (value == False): # indicating that the container at last status check was still running
                            localContainer = client.containers.get(key)
                            if (localContainer is not None):
                                #super().getLoggingObj().info(localContainer.logs())
                                #super().getLoggingObj().info(key + " : " + str(value) +  " : " + localContainer.status)
                                if (localContainer.status == "exited"): #update the value
                                    dictOfDockerContainerIds[key] = True
                                else: 
                                    allContainersHaveExited = False
                            else:
                                # WTF !!
                                super().getLoggingObj().error("Container Missing ::" + key)
                                return 0, 0, None

        
        # Write the log thingy now
        TotalNumberOfImagesDetected, detectedImages = self.totalNumberOfImagesDetected()
        elapsed_time = time.time() - start_time
        self.WriteLogsToDatabase(self.experimentName, elapsed_time, partOfFileName, detectedImages, TotalNumberOfImagesDetected, TotalImageCount, self.get_MessageId())
        return len(fileList), TotalNumberOfImagesDetected,  elapsed_time
    
    def totalNumberOfImagesDetected(self):
        internalTotalNumberOfImagesDetected = 0
        internaldetectedImages = []
        if (common._FileShare == False):
            for file in os.listdir(self.destinationFolder):
                jsonObject = {common._IMAGE_NAME_TAG: file, common._CONFIDENCE_SCORE_TAG:1}
                internaldetectedImages.append(jsonObject)
                internalTotalNumberOfImagesDetected +=1
        else:
            brv, desc, lst = self.storageSrv.getListOfAllFiles(common._FileShareName, self.destinationFolder)
            if (brv == True):
                if (not(lst is None or len(lst)<1)):
                    for i, imageFileName in enumerate(lst):
                        internalTotalNumberOfImagesDetected +=1
                        jsonObject = {common._IMAGE_NAME_TAG: imageFileName.name, common._CONFIDENCE_SCORE_TAG:1}
                        internaldetectedImages.append(jsonObject)
        return internalTotalNumberOfImagesDetected, internaldetectedImages


    def WriteLogsToDatabase(self, experimentName, elapsed_time, partOfFileName, detectedImages, TotalNumberOfImagesDetected, TotalImageCount, messageId = None):
        if (self.logResult == True):
            import datetime
            from  cosmosDBWrapper import clsCosmosWrapper

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
                            'param-partOfFileName' : partOfFileName,
                            common._MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID:messageId
                          }
            obj.logExperimentResult(documentDict= dictObject, removeExisting=False)





