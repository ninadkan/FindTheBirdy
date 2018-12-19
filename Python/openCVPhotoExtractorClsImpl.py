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


_NUMIMAGESTOCREATEMEANBACKGROUND = 10
_GRAYIMAGETHRESHOLD = 25
_NUMBEROFIMAGESTOPROCESS = -1
_BOUNDINGRECTANGLETHRESHOLD = 1000
_CONTOURCOUNTTHRESHOLD = 15
_MASKDIFFTHRESHOLD = 2
_WRITEOUTPUT = True # should we write the output file to destination folder or not
_LOGRESULT = True   # Should we write the results to CosmosDB or not. This is dependent on _WRITEOUTPUT values.
                    # as it looks at the files copied into destination folder
_VERBOSE = True     # verbosity. Set to True whilst debugging. Rest set to false. 



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
        return


    def processImages(self,imageBatchSize, partOfFileName=''):
        start_time = time.time()
        fileList = []
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
                    else:
                        fileList.append(file)        
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
                            else:
                                fileList.append(imageFileName.name)
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
        elapsed_time = time.time() - start_time

        return len(fileList), 0,  elapsed_time





