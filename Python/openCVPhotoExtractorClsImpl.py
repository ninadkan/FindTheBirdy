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


from pathlib import Path
import common
import docker_clsOpenCVProcessImages as ds
import azureFS.azureFileShareTest as fs


_LOGRESULT = True   # Should we write the results to CosmosDB or not. This is dependent on _WRITEOUTPUT values.
                    # as it looks at the files copied into destination folder



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
            for pos in range(0, l , imageBatchSize):
                objProc = ds.clsOpenCVProcessImages()
                objProc.processImages(  offset = pos, 
                                        imageSrcFolder = self.srcImageFolder,  
                                        imageDestinationFolder = self.destinationFolder, 
                                        experimentName = self.experimentName, 
                                        imageBatchSize = imageBatchSize, 
                                        partOfFileName=  partOfFileName)
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
                            'param-maskDiffThreshold' : sobjProc.get_maskDiffThreshold(),
                            'param-partOfFileName' : partOfFileName
                            }
            obj.logExperimentResult(documentDict= dictObject)





