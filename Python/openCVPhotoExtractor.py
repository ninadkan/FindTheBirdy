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
import os


from pathlib import Path
import common 

# Global parameters
g_fileList = []
g_grayMask = g_colourMask = None
g_srcImageFolder = None
g_filenameExtension = None
g_destinationFolder = None
g_verbosity = False
#defaults - applicable for Windows version only. override these with Linux versions

_HISTORYIMAGE = 10
_VARTHRESHOLD = 25
_NUMBEROFITERATIONS = -1
_BOUNDINGRECTANGLETHRESHOLD = 1300
_CONTOURCOUNTTHRESHOLD = 15
_MASKDIFFTHRESHOLD = 2
_PARTOFFILENAME = ''
_WRITEOUTPUT = True
_LOGRESULT = False
_EXPERIMENTNAME = ''

import logging
from loggingBase import getGlobalHandler, getGlobalLogObject, clsLoggingBase
g_logObj = getGlobalLogObject(__name__)



# https://www.pyimagesearch.com/2014/09/15/python-compare-two-images/
def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err

def init(partOfFileName=''):
    global g_fileList  
    global g_colourMask 
    global g_grayMask 
    global g_logObj

    g_fileList = [] 
    g_colourMask = None 
    g_grayMask = None 


    for file in os.listdir(g_srcImageFolder):
        if os.path.isfile(os.path.join(g_srcImageFolder,file)) and file.endswith(g_filenameExtension):
            if (len(partOfFileName) >0):
                if (partOfFileName in file):
                    g_fileList.append(file)
            else:
                g_fileList.append(file)

    if (len(g_fileList) == 0):
        g_logObj.error( "Error Loading file list")
        return 
    #select the ROI using the first image and use it to create mask
    filename= os.path.join(g_srcImageFolder, g_fileList[0])
    imgFirst = cv2.imread(filename)
    if (imgFirst is None):
        g_logObj.error(  "Unable to load " + filename)
    gray_image = cv2.cvtColor(imgFirst, cv2.COLOR_BGR2GRAY)

    # height and width is fixed for the image that we are capturing. 
    # It is same for all the images
    height, width = imgFirst.shape[:2]

    myROI = []

    #create mask to stub out areas that we don't want to include. 
    outFileName= os.path.join(g_srcImageFolder, 'mask_file.txt')
    with open(outFileName, 'r') as filehandle:  
        #places = [current_place.rstrip() for current_place in filehandle.readlines()]
        myROI = json.load(filehandle)

    if(myROI is None):
        g_logObj.error( "Unable to load MASK!!!")
        return
    if((len(myROI) == 0)):
        g_logObj.error(  "MASK Length is zero!!!")
        return

    #colour mask
    g_colourMask = imgFirst[0:height, 0:width]
    g_colourMask[:] = (255, 255,255) # change everything to white
    # Gray mask
    g_grayMask = gray_image[0:height, 0:width]
    g_grayMask[:] = 255 # change everything to white

    #create the masks
    cv2.fillPoly(g_grayMask, [np.array(myROI)],0)
    cv2.fillPoly(g_colourMask, [np.array(myROI)],0)

    return

    # ================================= Load Images and Create Mask ===============
    #endregion

def WriteOutputFile(imgColour, imageFileName, x, y, w, h, detectedImages, Padding=15):
    '''
    imgColour --> The bitwise representation of the coloured image
    imageFileName ; Filename of the image
    g_destinationFolder ; Where the images need to be copied
    x,y,w,h : bounding rectangles. 
    Padding: Required because the contour bounding rectangle is not big 
    enough for the images to be recognised
    '''
    global g_colourMask
    global g_logObj
    if ((imgColour is None):
        g_logObj.error(  "Invalid parameter imgColour")
        return None
    if(g_colourMask is None):
        g_logObj.error(  "Invalid parameter g_colourMask")
        return None
    
    ht, wt = imgColour.shape[:2]

    # mask not needed bits in the image
    imCrop = cv2.bitwise_and(imgColour, g_colourMask)
    
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
        outputFile = os.path.join(g_destinationFolder,imageFileName)
        cv2.imwrite(outputFile,frame)           
    return frame

def processImages(  historyImage = _HISTORYIMAGE, 
                    varThreshold = _VARTHRESHOLD, 
                    numberOfIterations = _NUMBEROFITERATIONS, 
                    boundingRectAreaThreshold = _BOUNDINGRECTANGLETHRESHOLD, 
                    contourCountThreshold = _CONTOURCOUNTTHRESHOLD,
                    maskDiffThreshold = _MASKDIFFTHRESHOLD,
                    partOfFileName= _PARTOFFILENAME,
                    writeOutput=_WRITEOUTPUT,
                    logResult = _LOGRESULT,
                    experimentName = ''):

    """
    processImages ; Processes photos and those that pass the various threshold tests 
                        are moved into the destination folder. 
    historyImage = The amount of images used to construct mean background"
    varThreshold = "Gray file threshold")
    numberOfIterations = -1 # positive value can be used to set the number of iterations. 
                            # Set this value to be more than the historyImage value
                            # useful for when you want to test against a small dataset
    boundingRectAreaThreshold = "minimum area of that a contour rectangle needs to have"
    contourCountThreshold = "Maximum number of contours that an image can have"
    maskDiffThreshold = "Minimum difference between two masks to distinguish the images"
    partOfFileName ="If you want to subselect file from the images folder, specify the partial name here"
    writeOutput = "specify if images in the output folder should be created; folder should exist")
    """
    # check how long it takes to run this 
    start_time = time.time()

    # update the location where our image can be found
    global g_srcImageFolder
    global g_destinationFolder
    global g_filenameExtension
    global g_logObj

    g_srcImageFolder = common._SRCIMAGEFOLDER 
    g_destinationFolder = common._DESTINATIONFOLDER
    g_filenameExtension = _FILENAMEEXTENSION = '.jpg'

    g_srcImageFolder = os.path.join(g_srcImageFolder,experimentName)

    # update the location where our output is to be written back
    
    g_destinationFolder = os.path.join(g_srcImageFolder,g_destinationFolder)

    if not os.path.exists(g_destinationFolder):
        g_logObj.info("creating folder {0}".format(g_destinationFolder))
        os.makedirs(g_destinationFolder)


    # Our background subtractor
    fgbg = cv2.createBackgroundSubtractorMOG2(  history=historyImage, 
                                                varThreshold=varThreshold, 
                                                detectShadows=False) 

    prevmask = None
    currentmask = None
    TotalNumberOfImagesDetected = 0

    # Test counters
    # false_positive = 0
    # false_negative = 0
    # true_true = 0 

    # Set to true if OpenCV thinks its detected a bird
    bOpenCVBirdDetected = False

    # Get the filelist, and mask images whilst initializing
    init(partOfFileName)
    detectedImages = []
    
    for i, imageFileName in enumerate(g_fileList):
        if ((numberOfIterations > 0) and (i > numberOfIterations)):
            break; # come of of the loop

        #print('.', end='', flush=True)

        filename = os.path.join(g_srcImageFolder, imageFileName)
        imgColour = cv2.imread(filename)  
        if (imgColour is None):
            g_logObj.error( "Unable to load " + filename)
            return None, None, None
        imgGray = cv2.cvtColor(imgColour, cv2.COLOR_BGR2GRAY)
        height, width = imgColour.shape[:2]
        imCrop = imgGray[0:int(height), 0:int(width)] #copy of the gray image 

        if (i == 0): #first time
            prevmask = imCrop[0:height, 0:width]
            prevmask[:] = 255 # change everything to white
        else:
            if (bOpenCVBirdDetected == False): #if the last one was a Bird then we don't move our previous g_grayMask
                prevmask = currentmask
    
        # apply the g_grayMask
        imCrop = cv2.bitwise_and(imCrop, g_grayMask)
        # apply background subtraction mean algorithm
        tempmask = fgbg.apply(imCrop)
    
        # remove noise from the image
        noiseremoved = cv2.medianBlur(tempmask,5)
        currentmask = cv2.medianBlur(noiseremoved,5)
    
        if (i >= historyImage):     # only once our background is well formed will we go ahead; meaning that the first 
                                    # historyImage number images should only contain the background
            #reset our flags
            bOpenCVBirdDetected = False
            # bBirdShouldBeDetected = False

            # strFileName = imageFileName.replace(g_filenameExtension,'')
            # if ((strFileName in DataClassification_Good)) :
            #     bBirdShouldBeDetected = True
 
            # calculate the difference
            diff = mse(currentmask, prevmask)

            contour_length = 0
            boundingRectArea = 0
                    
            if (diff > maskDiffThreshold): # passes the first test of difference
                    ret, thresh = cv2.threshold(currentmask, varThreshold, 255, 0)
                    contours = None
                    hierarchy = None
                    if (os.name == "posix"): # differences in implementations
                        contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                    else:
                        im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                    contour_length = len(contours)
                    if (not (contour_length == 0 or contour_length > contourCountThreshold)): 
                        # passes second test of contour length 
                        cntsSorted = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
                        for j, cnt in enumerate(cntsSorted):
                            if ((j > contourCountThreshold) or (bOpenCVBirdDetected == True)): 
                                break
                            (x,y,w,h) = cv2.boundingRect(cnt)
                            boundingRectArea = w*h 
                            if (boundingRectArea > boundingRectAreaThreshold):
                                # passed the test of minimum bounding area 
                                bOpenCVBirdDetected = True
                                TotalNumberOfImagesDetected = TotalNumberOfImagesDetected +1
                                
                                if (writeOutput == True):
                                    WriteOutputFile(imgColour, imageFileName, x, y, w, h, detectedImages)
                            else:   # we've already reached the end as we are sorted and 
                                    # assume that boundingRectArea and boundingRect area are related. 
                                break 
        
            if (g_verbosity == True):
                g_logObj.info("")
                g_logObj.info(">>> Debugging image = {0}, Contour Length = {1:0.4f}, last boundingRectArea = {2:0.4f}, OpenCVDetected = {3}, diff = {4:0.4f}".format(imageFileName, contour_length, boundingRectArea, bOpenCVBirdDetected, diff))

    elapsed_time = time.time() - start_time

    if (logResult == True):
        import datetime
        from  cosmosDBWrapper import clsCosmosWrapper
        obj = clsCosmosWrapper()
        dictObject = {  common._IMAGE_DETECTION_PROVIDER_TAG : __name__,
                        common._EXPERIMENTNAME_TAG : experimentName,
                        common._DATETIME_TAG : str(datetime.datetime.now()),
                        common._ELAPSED_TIME_TAG : elapsed_time,
                        common._DETECTED_IMAGES_TAG : detectedImages,
                        'result-totalNumberOfRecords': len(g_fileList),
                        'TotalNumberOfImagesDetected' : TotalNumberOfImagesDetected,
                        # 'result-true_true': true_true,
                        # 'result-false_positive': false_positive,
                        # 'result-false_negative': false_negative,
                        'param-historyImage' : historyImage, 
                        'param-varThreshold' : varThreshold, 
                        'param-numberOfIterations' : numberOfIterations, 
                        'param-boundingRectAreaThreshold' : boundingRectAreaThreshold, 
                        'param-contourCountThreshold' : contourCountThreshold,
                        'param-maskDiffThreshold' : maskDiffThreshold,
                        'param-partOfFileName' : partOfFileName
                        }
        obj.logExperimentResult(documentDict= dictObject, removeExisting=False)
    return len(g_fileList), TotalNumberOfImagesDetected,  elapsed_time  #, true_true, false_positive, false_negative

if __name__ == "__main__":
    #python openCVPhotoExtractor.py processImages
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser = argparse.ArgumentParser(description=__doc__,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose", help="increase output verbosity",action="store_true")
    subparsers = parser.add_subparsers(dest="command")
    process_parser = subparsers.add_parser("processImages", help=processImages.__doc__)

    process_parser.add_argument("srcImageFolder", nargs='?', default=common._SRCIMAGEFOLDER, help="Source Folder")
    process_parser.add_argument("filenameExtension", nargs='?',default=_FILENAMEEXTENSION, help="file extension that needs to be copied")
    process_parser.add_argument("destinationFolder", nargs='?', default=common._DESTINATIONFOLDER, help="Destination Folder")
    process_parser.add_argument("historyImage", nargs='?', default=_HISTORYIMAGE, help="The amount of images used to construct mean background")
    process_parser.add_argument("varThreshold", nargs='?',default=_VARTHRESHOLD, help="Gray file threshold")
    process_parser.add_argument("numberOfIterations", nargs='?', default=_NUMBEROFITERATIONS, help="Number of files to be scanned. -1 for all, 0 for one")
    process_parser.add_argument("boundingRectAreaThreshold", nargs='?', default=_BOUNDINGRECTANGLETHRESHOLD, help="minimum area of that a contour rectangle needs to have")
    process_parser.add_argument("contourCountThreshold", nargs='?',default=_CONTOURCOUNTTHRESHOLD, help="Maximum number of contours that an image can have")
    process_parser.add_argument("maskDiffThreshold", nargs='?', default=_MASKDIFFTHRESHOLD, help="Minimum difference between two masks to distinguish the images")
    process_parser.add_argument("partOfFileName", nargs='?',default=_PARTOFFILENAME, help="If you want to subselect file from the images folder, specify the partial name here")
    process_parser.add_argument("writeOutput", nargs='?', default=_WRITEOUTPUT, help="To create the images in the output folder")
    process_parser.add_argument("logResult", nargs='?', default=_LOGRESULT, help="Log result to Azure cosmos DB")
    process_parser.add_argument("experimentName", nargs='?', default=_EXPERIMENTNAME, help="Log result to Azure cosmos DB")
    
    
    args = parser.parse_args()
    if args.command == "processImages":
        g_srcImageFolder = args.srcImageFolder
        g_filenameExtension = args.filenameExtension
        g_destinationFolder = args.destinationFolder

        if (args.verbose):
            g_verbosity = True

        l,tt, t, = processImages(   historyImage = args.historyImage, 
                                            varThreshold=args.varThreshold, 
                                            numberOfIterations=args.numberOfIterations,
                                            boundingRectAreaThreshold=args.boundingRectAreaThreshold, 
                                            contourCountThreshold=args.contourCountThreshold, 
                                            maskDiffThreshold=args.maskDiffThreshold,
                                            partOfFileName=args.partOfFileName, 
                                            writeOutput=args.writeOutput,
                                            logResult = args.logResult,
                                            experimentName = args.experimentName )


        print ("")
        print("Elapsed time = " + time.strftime("%H:%M:%S", time.gmtime(t))+ "Total images processed = {0}, detected = {1}".format(l, tt))                            

            

