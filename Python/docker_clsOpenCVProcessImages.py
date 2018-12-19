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
import azureFS.azureFileShareTest as fs
import azureFS.mask_creation as mask
import azureFS.azureCommon as azcommon


_NUMIMAGESTOCREATEMEANBACKGROUND = 10
_GRAYIMAGETHRESHOLD = 25
_NUMBEROFIMAGESTOPROCESS = -1
_BOUNDINGRECTANGLETHRESHOLD = 1000
_CONTOURCOUNTTHRESHOLD = 15
_MASKDIFFTHRESHOLD = 2

_WRITEOUTPUT = True # should we write the output file to destination folder or not
_VERBOSE = True     # verbosity. Set to True whilst debugging. Rest set to false. 



class clsOpenCVProcessImages:
    def __init__(self):
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
            brv, desc, lst = fs.getListOfAllFiles(common._FileShareName, imageSrcFolder)
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
                    print("Directory is either None or zero order")
            else:
                print("fs.getListOfAllFiles returned False")
    

    

        # figure out the images that we need to process
        self.listOfImagesToBeProcessed = []
        if (offset > self.numImagesToCreateMeanBackground):
            self.listOfImagesToBeProcessed = completefileList[offset-self.numImagesToCreateMeanBackground:offset + imageBatchSize]
        else:
            # this is usually for the first time execution when offset = 0
            self.listOfImagesToBeProcessed = completefileList[offset:offset + imageBatchSize]
    
        print(offset)
        print(imageBatchSize)
        print(len(self.listOfImagesToBeProcessed))
        # check ok
        assert(len(self.listOfImagesToBeProcessed)> self.numImagesToCreateMeanBackground), "Number of Images passed are less than required to create background"

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
            print('.', end='', flush=True)

            imgColour = None
            if (common._FileShare == False):
                imgColour = cv2.imread(os.path.join(imageSrcFolder, imageFileName))  
            else:
                brv, desc, imgColour = mask.GetRawImage(common._FileShareName, imageSrcFolder, imageFileName)
                assert(brv == True), "Unable to load " + imageFileName

            assert(imgColour is not None), "Unable to load " + imageFileName
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
                        ret, thresh = cv2.threshold(currentmask, self.grayImageThreshold, 255, 0)
                        im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                        contour_length = len(contours)
                        if (not (contour_length == 0 or contour_length > self.contourCountThreshold)): 
                            # passes second test of contour length 
                            cntsSorted = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
                            for j, cnt in enumerate(cntsSorted):
                                if ((j > self.contourCountThreshold) or (bOpenCVBirdDetected == True)): 
                                    # we don't continue if previous one had found the object! 
                                    break
                                (x,y,w,h) = cv2.boundingRect(cnt)
                                boundingRectArea = w*h 
                                if (boundingRectArea > self.boundingRectAreaThreshold):
                                    # passed the test of minimum bounding area 
                                    bOpenCVBirdDetected = True
                                    TotalNumberOfImagesDetected = TotalNumberOfImagesDetected +1
                                    
                                    if (self.writeOutput == True):
                                        self.WriteOutputFile(imgColour, imageFileName, x, y, w, h, detectedImages)
                                else:   # we've already reached the end as we are sorted and 
                                        # assume that boundingRectArea and boundingRect area are related. 
                                    break 
            
                if (self.verbosity == True):
                    print("")
                    print(">>> Debugging image = {0}, Contour Length = {1:0.4f}, last boundingRectArea = {2:0.4f}, OpenCVDetected = {3}, diff = {4:0.4f}".format(imageFileName, contour_length, boundingRectArea, bOpenCVBirdDetected, diff))

        elapsed_time = time.time() - start_time

        self.WriteLogsToDatabase(experimentName, elapsed_time, partOfFileName, detectedImages, TotalNumberOfImagesDetected)

        return len(self.listOfImagesToBeProcessed), TotalNumberOfImagesDetected,  elapsed_time  #, true_true, false_positive, false_negative

    def createMask(self):
        self.g_colourMask = None 
        self.g_grayMask = None 

        assert(self.listOfImagesToBeProcessed is not None), "FileList is None whilest invoking createMask"
        assert(len(self.listOfImagesToBeProcessed) > 0), "FileList length is 0!"
        #select the ROI using the first image and use it to create mask

        imgFirst = None
        if (common._FileShare == False):
            imgFirst = cv2.imread(os.path.join(self.imageSrcFolder, self.listOfImagesToBeProcessed[0]))  
        else:
            brv, desc, imgFirst = mask.GetRawImage(common._FileShareName, self.imageSrcFolder, self.listOfImagesToBeProcessed[0])
            assert(brv == True), "Unable to load " + imageFileName

        assert(imgFirst is not None), "Unable to load " + self.listOfImagesToBeProcessed[0]
        gray_image = cv2.cvtColor(imgFirst, cv2.COLOR_BGR2GRAY)

        # height and width is fixed for the image that we are capturing. 
        # It is same for all the images
        height, width = imgFirst.shape[:2]

        myROI = []

        #create mask to stub out areas that we don't want to include. 
        if (common._FileShare == False):
            outFileName= os.path.join(self.imageSrcFolder, azcommon.maskFileName)
            with open(outFileName, 'r') as filehandle:  
                myROI = json.load(filehandle)
        else:
            brv, desc, myROI = fs.getMaskFileContent(common._FileShareName, self.imageSrcFolder)
            assert(brv == True), "Unable to load " + azcommon.maskFileName

        assert(myROI is not None), "Unable to load MASK!!!"
        assert((len(myROI)> 0)), "MASK Length is zero!!!"

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
        
        assert(imgColour is not None), "Invalid parameter imgColour"
        assert(self.g_colourMask is not None), "Invalid parameter self.g_colourMask"
        
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
                print("Saving data, filename = {0}".format(imageFileName))
                brv, desc, myROI = fs.saveFileImage(common._FileShareName, self.imageDestinationFolder, imageFileName, data )
                assert(brv == True), "Unable to save image file " + imageFileName
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



if __name__ == "__main__":
    # python docker_clsOpenCVProcessImages.py -v processImages 2018-04-16 
    # python docker_clsOpenCVProcessImages.py -v processImages 2018-04-16 50
    # python docker_clsOpenCVProcessImages.py -v processImages 2018-04-16 50 25 20
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser = argparse.ArgumentParser(description=__doc__,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose", help="increase output verbosity",action="store_true")
    subparsers = parser.add_subparsers(dest="command")
    process_parser = subparsers.add_parser("processImages", help=clsOpenCVProcessImages.processImages.__doc__)

    # necessary arguments
    process_parser.add_argument(common._ARGS_EXPERIMENT_NAME,nargs='?',help="Name of folder where experiment images are copied")
    process_parser.add_argument(common._ARGS_OFFSET, type=int, nargs='?', default=0, help="offset from image list")
    process_parser.add_argument(common._ARGS_BATCH_SIZE, type=int, nargs='?', default=common._BATCH_SIZE, help="Number of images to be scanned in one execution")
    process_parser.add_argument(common._ARGS_NUMBER_OF_IMAGES_TO_PROCESS, type=int, nargs='?', default=-1, help="Number of files to be scanned. -1 for all, 0 for one")    
    process_parser.add_argument(common._ARGS_SRC_IMAGE_FOLDER, nargs='?', default=common._SRCIMAGEFOLDER, help="Source Folder")
    process_parser.add_argument(common._ARGS_DESTINATION_FOLDER, nargs='?', default=common._DESTINATIONFOLDER, help="Destination Folder")
    process_parser.add_argument(common._ARGS_FILE_NAME_EXTENSTION, nargs='?',default=common._FILENAMEEXTENSION, help="file extension that needs to be copied")
    process_parser.add_argument(common._ARGS_PART_OF_FILE_NAME, nargs='?',default=common._PARTOFFILENAME, help="If you want to subselect file from the images folder, specify the partial name here")


    # extra arguments
    process_parser.add_argument(common._ARGS_NUM_IMAGES_TO_CREATE_BKGRND, type=int, nargs='?', default=_NUMIMAGESTOCREATEMEANBACKGROUND, help="The amount of images used to construct mean background")
    process_parser.add_argument(common._ARGS_GRAY_THRESHOLD, type=int, nargs='?',default=_GRAYIMAGETHRESHOLD, help="Gray file threshold")
    process_parser.add_argument(common._ARGS_BOUNDING_RECT_AREA_THRESHOLD,type=int,  nargs='?', default=_BOUNDINGRECTANGLETHRESHOLD, help="minimum area of that a contour rectangle needs to have")
    process_parser.add_argument(common._ARGS_CONTOUR_COUNT_THRESHOLD, type=int,  nargs='?',default=_CONTOURCOUNTTHRESHOLD, help="Maximum number of contours that an image can have")
    process_parser.add_argument(common._ARGS_MASK_DIFF_THRESHOLD, type=int,  nargs='?', default=_MASKDIFFTHRESHOLD, help="Minimum difference between two masks to distinguish two images")
    process_parser.add_argument(common._ARGS_WRITE_OUTPUT, nargs='?', default=_WRITEOUTPUT, help="True specifies that images should be copied to output folder")
    
    args = parser.parse_args()
    if args.command == "processImages":

        # print("numImagesToCreateMeanBackground: {0}".format(args.numImagesToCreateMeanBackground))
        # print("grayImageThreshold: {0}".format(args.grayImageThreshold))
        # print("boundingRectAreaThreshold: {0}".format(args.boundingRectAreaThreshold))
        # print("contourCountThreshold: {0}".format(args.contourCountThreshold))
        # print("maskDiffThreshold: {0}".format(args.maskDiffThreshold))
        # print("writeOutput: {0}".format(args.writeOutput))
        # print("verbose: {0}".format(args.verbose))
        # print("srcImageFolder: {0}".format(args.srcImageFolder))
        # print("experimentName: {0}".format(args.experimentName))
        # print("offset: {0}".format(args.offset))
        # print("destinationFolder: {0}".format(args.destinationFolder))
        # print("imageBatchSize: {0}".format(args.imageBatchSize))
        # print("partOfFileName: {0}".format(args.partOfFileName))
        # print("numberOfImagesToProcess: {0}".format(args.numberOfImagesToProcess))

        objProc = clsOpenCVProcessImages()

        objProc.set_numImagesToCreateMeanBackground(args.numImagesToCreateMeanBackground)
        objProc.set_grayImageThreshold(args.grayImageThreshold)
        objProc.set_boundingRectAreaThreshold(args.boundingRectAreaThreshold)
        objProc.set_contourCountThreshold(args.contourCountThreshold)
        objProc.set_maskDiffThreshold(args.maskDiffThreshold)
        objProc.set_writeOutput(args.writeOutput)

        if (args.verbose):
            objProc.set_verbosity(True)
        else:
            objProc.set_verbosity(False)
            
        # Important, that the structure of images to be loaded is pre-defined. 
        # Now the srcImageFolder contains the final directory name. 

        srcImageFolder = None
        destinationFolder = None
        if (common._FileShare == False):
            srcImageFolder = os.path.join(str(args.srcImageFolder),str(args.experimentName))
            destinationFolder = os.path.join(srcImageFolder,args.destinationFolder)
            if not os.path.exists(destinationFolder):
                print("creating folder {0}".format(destinationFolder))
                os.makedirs(destinationFolder)    
        else:
            srcImageFolder = str(args.srcImageFolder) + "/" + str(args.experimentName)
            destinationFolder = srcImageFolder + "/" + args.destinationFolder
            brv, desc, myROI  = fs.createDirectory(common._FileShareName, destinationFolder)
            assert(brv == True), "Unable to create/locate output directory " + destinationFolder



        l, tt, t = objProc.processImages(   offset = int(args.offset), 
                                            imageSrcFolder = str(srcImageFolder),  
                                            imageDestinationFolder = str(destinationFolder), 
                                            experimentName = str(args.experimentName), 
                                            imageBatchSize = int(args.imageBatchSize), 
                                            partOfFileName=  str(args.partOfFileName),
                                            numberOfImagesToProcess = int(args.numberOfImagesToProcess) )

        print ("")
        print("Elapsed time = " + time.strftime("%H:%M:%S", time.gmtime(t))+ "; Total images processed = {0}, detected = {1}".format(l, tt))                            






