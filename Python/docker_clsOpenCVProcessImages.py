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
# import azureFS.azureFileShareTest as fs
# import azureFS.mask_creation as mask
# import azureFS.azureCommon as azcommon
import storageFileService as sf
import cosmosStatusUpdate as cf
import uuid


_NUMIMAGESTOCREATEMEANBACKGROUND = 10
_GRAYIMAGETHRESHOLD = 25
_NUMBEROFIMAGESTOPROCESS = -1
_BOUNDINGRECTANGLETHRESHOLD = 1000
_CONTOURCOUNTTHRESHOLD = 15
_MASKDIFFTHRESHOLD = 2

_WRITEOUTPUT = True # should we write the output file to destination folder or not
_VERBOSE = True     # verbosity. Set to True whilst debugging. Rest set to false. 

import logging
from loggingBase import clsLoggingBase



class clsOpenCVProcessImages(clsLoggingBase):
    def __init__(self):

        super().__init__(__name__)
        # image processing init parameters
        self.numImagesToCreateMeanBackground = _NUMIMAGESTOCREATEMEANBACKGROUND
        self.grayImageThreshold =  _GRAYIMAGETHRESHOLD
        self.boundingRectAreaThreshold = _BOUNDINGRECTANGLETHRESHOLD
        self.contourCountThreshold = _CONTOURCOUNTTHRESHOLD
        self.maskDiffThreshold = _MASKDIFFTHRESHOLD
        # Mask Parameter
        self.g_grayMask = self.g_colourMask = None

        # Environmental parameters
        self.listOfImagesToBeProcessed = None
        self.imageSrcFolder = None
        self.imageDestinationFolder = None
        self.filenameExtension = common._FILENAMEEXTENSION

        # Logging Paramters
        self.writeOutput=_WRITEOUTPUT
        self.verbosity = _VERBOSE
        self.writeBuffer = 15 # after every 15 items, we'll write the status to database

        #tracking progress Ids
        self.messageID = ''

        #Storage and cosmos Object
        self.storageSrv = sf.storageFileService(None)
        self.cosmosStatusObj = cf.clsStatusUpdate()
        

        return

    def get_numImagesToCreateMeanBackground(self):
        return self.numImagesToCreateMeanBackground
    def get_grayImageThreshold(self):
        return self.grayImageThreshold
    def get_boundingRectAreaThreshold(self):
        return self.boundingRectAreaThreshold 
    def get_contourCountThreshold(self):
        return self.contourCountThreshold
    def get_maskDiffThreshold(self):
        return self.maskDiffThreshold
    def get_writeOutput(self):
        return self.writeOutput
    def get_verbosity(self):
        return self.verbosity 
    def get_MessageId(self):
        return self.messageID


    def set_numImagesToCreateMeanBackground(self, value):
        self.numImagesToCreateMeanBackground = value
        return
    def set_grayImageThreshold(self, value):
        self.grayImageThreshold  = value
        return
    def set_boundingRectAreaThreshold(self, value):
        self.boundingRectAreaThreshold  = value
        return
    def set_contourCountThreshold(self, value):
        self.contourCountThreshold  = value
        return
    def set_maskDiffThreshold(self, value):
        self.maskDiffThreshold  = value
        return
    def set_writeOutput(self, value):
        self.writeOutput  = value
        return
    def set_verbosity(self, value):
        self.verbosity = value
        return
    def set_MessageId(self, value):
        self.messageID = value
        return


    def processImages(  self, 
                        offset, 
                        imageSrcFolder,  
                        imageDestinationFolder, 
                        experimentName, 
                        imageBatchSize, 
                        partOfFileName= '', 
                        numberOfImagesToProcess=-1):

        """
        processImages ; Processes photos and those that pass the various threshold tests 
                            are moved into the destination folder. 
        numImagesToCreateMeanBackground = The amount of images used to construct mean background"
        grayImageThreshold = "Gray image threshold")
        numberOfImagesToProcess = -1 # positive value can be used to set the number of iterations. 
                                # Set this value to be more than the numImagesToCreateMeanBackground value
                                # useful for when you want to test against a small dataset
        boundingRectAreaThreshold = "minimum area of that a contour rectangle needs to have"
        contourCountThreshold = "Maximum number of contours that an image can have; If there are too many, its too fragmented so we ignore it"
        maskDiffThreshold = "Minimum difference between two masks to distinguish the images"
        partOfFileName ="If you want to subselect file from the images folder, specify the partial name here"
        writeOutput = "specify if images in the output folder should be created; folder should exist")
        """

        # check how long it takes to run this 
        start_time = time.time()

        # First add all the images that are in the source folder
        completefileList = []

        if (common._FileShare == False):
            lst = []
            lst = os.listdir(imageSrcFolder)
            for file in lst:
                if file.endswith(self.filenameExtension):
                    if (len(partOfFileName) >0):
                        if (partOfFileName in file):
                            completefileList.append(file)
                    else:
                        completefileList.append(file)       
        else:
            lst = []
            brv, desc, lst = self.storageSrv.getListOfAllFiles(common._FileShareName, imageSrcFolder)
            if (brv == True):
                if (not(lst is None or len(lst)<1)):
                    for i, imageFileName in enumerate(lst):
                        if (imageFileName.name.endswith(self.filenameExtension)):
                            if (len(partOfFileName) >0):
                                if (partOfFileName in imageFileName.name):
                                    completefileList.append(imageFileName.name)
                            else:
                                completefileList.append(imageFileName.name)
                else:
                    super().getLoggingObj().warn("Directory is either None or zero order")
            else:
                super().getLoggingObj().warn("self.storageSrv.getListOfAllFiles returned False")

        # figure out the images that we need to process
        self.listOfImagesToBeProcessed = []
        if (offset > self.numImagesToCreateMeanBackground):
            self.listOfImagesToBeProcessed = completefileList[offset-self.numImagesToCreateMeanBackground:offset + imageBatchSize]
        else:
            # this is usually for the first time execution when offset = 0
            self.listOfImagesToBeProcessed = completefileList[offset:offset + imageBatchSize]
    
        #super().getLoggingObj().warn(offset)
        #super().getLoggingObj().warn(imageBatchSize)
        #super().getLoggingObj().warn(len(self.listOfImagesToBeProcessed))
        # check ok
        if (len(self.listOfImagesToBeProcessed)< self.numImagesToCreateMeanBackground):
            super().getLoggingObj().error("Number of Images passed are less than required to create background")
            

        # update the location where our image can be found
        self.imageSrcFolder = imageSrcFolder
        self.imageDestinationFolder = imageDestinationFolder

        # Our background subtractor
        fgbg = cv2.createBackgroundSubtractorMOG2(  history=self.numImagesToCreateMeanBackground, 
                                                    varThreshold=self.grayImageThreshold, 
                                                    detectShadows=False) 
        prevmask = None
        currentmask = None
        TotalNumberOfImagesDetected = 0

        # Set to true if OpenCV thinks its detected a bird
        bOpenCVBirdDetected = False

        # # Get the filelist, and mask images whilst createMaskializing
        self.createMask()
        detectedImages = []
        
        for i, imageFileName in enumerate(self.listOfImagesToBeProcessed):
            if ((numberOfImagesToProcess > 0) and (i > numberOfImagesToProcess)):
                break; # come of of the loop

            if (i % self.writeBuffer ==0 ):
                self.writeProgressLogToDatabase(experimentName,offset, i , len(self.listOfImagesToBeProcessed), '',  "OK")


            #print('.', end='', flush=True)

            imgColour = None
            if (common._FileShare == False):
                imgColour = cv2.imread(os.path.join(imageSrcFolder, imageFileName))  
            else:
                brv, desc, imgColour = self.storageSrv.GetRawImage(common._FileShareName, imageSrcFolder, imageFileName)
                if(brv == False):
                    super().getLoggingObj().error("Unable to load " + imageFileName)
                    return None, None, None

            if(imgColour is None):
                super().getLoggingObj().error("Unable to load " + imageFileName)
                return None, None, None

            imgGray = cv2.cvtColor(imgColour, cv2.COLOR_BGR2GRAY)
            height, width = imgColour.shape[:2]
            imCrop = imgGray[0:int(height), 0:int(width)] #copy of the gray image 

            if (i == 0): #first time
                prevmask = imCrop[0:height, 0:width]
                prevmask[:] = 255 # change everything to white
            else:
                if (bOpenCVBirdDetected == False): #if the last one was a Bird then we don't move our previous self.g_grayMask
                    prevmask = currentmask
        
            # apply the self.g_grayMask
            imCrop = cv2.bitwise_and(imCrop, self.g_grayMask)
            # apply background subtraction mean algorithm
            tempmask = fgbg.apply(imCrop)
        
            # remove noise from the image
            noiseremoved = cv2.medianBlur(tempmask,5)
            currentmask = cv2.medianBlur(noiseremoved,5)
        
            if (i >= self.numImagesToCreateMeanBackground):     
                # only once our background is well formed will we go ahead; meaning that the first 
                # numImagesToCreateMeanBackground number images should only contain the background
                #reset our flags
                bOpenCVBirdDetected = False
     
                # calculate the difference
                diff = self.mse(currentmask, prevmask)

                contour_length = 0
                boundingRectArea = 0
                        
                if (diff > self.maskDiffThreshold): # passes the first test of difference
                        #print('Passed first threshold')
                        ret, thresh = cv2.threshold(currentmask, self.grayImageThreshold, 255, 0)
                        contours = None
                        hierarchy = None
                        if (os.name == "posix"): # differences in implementations
                            contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                        else:
                            im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                        contour_length = len(contours)
                        if (not (contour_length == 0 or contour_length > self.contourCountThreshold)):
                            #print('passes second test of contour length')
                            cntsSorted = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
                            for j, cnt in enumerate(cntsSorted):
                                if ((j > self.contourCountThreshold) or (bOpenCVBirdDetected == True)): 
                                    # we don't continue if previous one had found the object! 
                                    break
                                (x,y,w,h) = cv2.boundingRect(cnt)
                                boundingRectArea = w*h 
                                if (boundingRectArea > self.boundingRectAreaThreshold):
                                    #print(' passed the test of minimum bounding area ')
                                    bOpenCVBirdDetected = True
                                    TotalNumberOfImagesDetected = TotalNumberOfImagesDetected +1
                                    
                                    if (self.writeOutput == True):
                                        self.WriteOutputFile(imgColour, imageFileName, x, y, w, h, detectedImages)
                                else:   # we've already reached the end as we are sorted and 
                                        # assume that boundingRectArea and boundingRect area are related. 
                                    break 
            
                if (self.verbosity == True):
                    super().getLoggingObj().info("")
                    super().getLoggingObj().info(">>> Debugging image = {0}, Contour Length = {1:0.4f}, last boundingRectArea = {2:0.4f}, OpenCVDetected = {3}, diff = {4:0.4f}".format(imageFileName, contour_length, boundingRectArea, bOpenCVBirdDetected, diff))

        elapsed_time = time.time() - start_time
        self.writeProgressLogToDatabase(experimentName,offset, len(self.listOfImagesToBeProcessed) , len(self.listOfImagesToBeProcessed), elapsed_time,  "OK")
        return len(self.listOfImagesToBeProcessed), TotalNumberOfImagesDetected,  elapsed_time  #, true_true, false_positive, false_negative

    def writeProgressLogToDatabase(self, experimentName, offset, currentCount=-1, maxItems=-1, elapsed_time='',  statusMessage=''):
        #objRun = cosmosDB.cosmosStatusUpdate.clsStatusUpdate() 
        self.cosmosStatusObj.insert_document(self.messageID, experimentName, offset, currentCount, maxItems, elapsed_time, statusMessage )        
        return

    def createMask(self):
        self.g_colourMask = None 
        self.g_grayMask = None 

        if(self.listOfImagesToBeProcessed is None):
            super().getLoggingObj().error("FileList is None whilest invoking createMask")
            return
        if (len(self.listOfImagesToBeProcessed) == 0):
            super().getLoggingObj().error("FileList length is 0!")
            return
        #select the ROI using the first image and use it to create mask

        imgFirst = None
        if (common._FileShare == False):
            imgFirst = cv2.imread(os.path.join(self.imageSrcFolder, self.listOfImagesToBeProcessed[0]))  
        else:
            brv, desc, imgFirst = self.storageSrv.GetRawImage(common._FileShareName, self.imageSrcFolder, self.listOfImagesToBeProcessed[0])
            if(brv == False):
                super().getLoggingObj().error("Unable to load " + imageFileName)
                return

        if(imgFirst is None):
            super().getLoggingObj().error("Unable to load " + self.listOfImagesToBeProcessed[0])
            return
        gray_image = cv2.cvtColor(imgFirst, cv2.COLOR_BGR2GRAY)

        # height and width is fixed for the image that we are capturing. 
        # It is same for all the images
        height, width = imgFirst.shape[:2]

        myROI = []

        #create mask to stub out areas that we don't want to include. 
        if (common._FileShare == False):
            outFileName= os.path.join(self.imageSrcFolder, self.storageSrv.maskFileName)
            with open(outFileName, 'r') as filehandle:  
                myROI = json.load(filehandle)
        else:
            brv, desc, myROI = self.storageSrv.getMaskFileContent(common._FileShareName, self.imageSrcFolder)
            if(brv == False):
                super().getLoggingObj().error("Unable to load " + self.storageSrv.maskFileName)
                return

        if (myROI is None):
            super().getLoggingObj().error( "Unable to load MASK!!!")
            return
        if((len(myROI) == 0)):
            super().getLoggingObj().error( "MASK Length is zero!!!")
            return

        #colour mask
        self.g_colourMask = imgFirst[0:height, 0:width]
        self.g_colourMask[:] = (255, 255,255) # change everything to white
        # Gray mask
        self.g_grayMask = gray_image[0:height, 0:width]
        self.g_grayMask[:] = 255 # change everything to white

        #create the masks
        cv2.fillPoly(self.g_grayMask, [np.array(myROI)],0)
        cv2.fillPoly(self.g_colourMask, [np.array(myROI)],0)

        return

    def WriteOutputFile(self,imgColour, imageFileName, x, y, w, h, detectedImages, Padding=15):
        '''
        imgColour --> The bitwise representation of the coloured image
        imageFileName ; Filename of the image
        self.imageDestinationFolder ; Where the images need to be copied
        x,y,w,h : bounding rectangles. 
        Padding: Required because the contour bounding rectangle is not big 
        enough for the images to be recognised
        '''
        #super().getLoggingObj().warn('WriteOutputFile...')
        if(imgColour is None):
            super().getLoggingObj().error( "Invalid parameter imgColour")
            return None
        if (self.g_colourMask is None):
            super().getLoggingObj().error( "Invalid parameter self.g_colourMask")
            return None
        
        ht, wt = imgColour.shape[:2]

        # mask not needed bits in the image
        imCrop = cv2.bitwise_and(imgColour, self.g_colourMask)
        
        # # add padding and manage crop dimensions
        # I think because of the aspect ratio, we need to padd more to height
        TopX = x-(3*Padding) if ((x-(3*Padding)) >= 0) else 0
        TopY = y- (6*Padding) if ((y-6*Padding) >= 0 ) else ht
        BottomX = x + (3*Padding)  + w if ((x + (3*Padding)  + w)<= wt) else wt
        BottomY = y + (6*Padding) + h if ((y + (6*Padding) + h) <= ht) else ht
        
        detectedImages.append({ common._IMAGE_NAME_TAG:imageFileName,
                                'TopX': TopX, 
                                'TopY': TopY, 
                                'BottomX' : BottomX, 
                                'BottomY' :BottomY  })
        #crop the frame
        frame = imCrop[TopY:BottomY, TopX:BottomX]

        if frame is not None and frame.size > 0: # otherwise we had couple of instances when the image file was of size 0!!!
            if (common._FileShare == False):
                outputFile = os.path.join(self.imageDestinationFolder,imageFileName)
                cv2.imwrite(outputFile,frame)           
            else:
                data = cv2.imencode(common._FILENAMEEXTENSION, frame)[1].tostring()
                #super().getLoggingObj().warn("Saving data, filename = {0}".format(imageFileName))
                brv, desc, myROI = self.storageSrv.saveFileImage(common._FileShareName, self.imageDestinationFolder, imageFileName, data )
                if(brv == False):
                    super().getLoggingObj().error( "Unable to save image file " + imageFileName)
                    return None
        #super().getLoggingObj().warn('...WriteOutputFile')
        return frame


    # https://www.pyimagesearch.com/2014/09/15/python-compare-two-images/
    def mse(self,imageA, imageB):
        # the 'Mean Squared Error' between the two images is the
        # sum of the squared difference between the two images;
        # NOTE: the two images must have the same dimension
        err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        err /= float(imageA.shape[0] * imageA.shape[1])
        
        # return the MSE, the lower the error, the more "similar"
        # the two images are
        return err


