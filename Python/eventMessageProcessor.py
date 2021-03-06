

import os
import sys
#import logging
import time
#from azure.eventhub import EventHubClient, Receiver, Offset
import json
#import argparse
#import requests
import common
import openCVPhotoExtractorTest as test
import openCVPhotoExtractorClsImpl
import docker_clsOpenCVProcessImages
import asyncio

import logging
from loggingBase import getGlobalHandler, getGlobalLogObject, clsLoggingBase
g_logObj = getGlobalLogObject(__name__)

dummySleep=1
# ============================ start Experiment Message ============================ #

async def processStartExperimentMessage(msgBody):
    global g_logObj
    brv = False
    experimentName = msgBody[common._MESSAGE_TYPE_START_EXPERIMENT_EXPERIMENT_NAME]

    g_logObj.info("Start Experiment Message Received ... {} {} {}".format( msgBody[common._MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID], 
                                                                        msgBody[common._MESSAGE_TYPE_START_EXPERIMENT_EXPERIMENT_NAME ],
                                                                        msgBody[common._MESSAGE_TYPE_START_EXPERIMENT_CREATION_DATE_TIME ]))    
    if (experimentName is None):
        g_logObj.error("No experiment name passed!")
        return brv
    brv = test.delete_existing_files(experimentName)
    if (brv == True):
        # send messages to start processing the images,
        procObject = openCVPhotoExtractorClsImpl.clsOpenCVObjectDetector(experimentName=experimentName)
        procObject.set_MessageId(msgBody[common._MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID])
        #l, tt,  t = procObject.processImages(partOfFileName='2018-12-14_04')
        l, tt,  t = await procObject.processImages()
        g_logObj.warn ("Return from processStartExperimentMessage!!!")
        g_logObj.warn("Elapsed time = " + time.strftime("%H:%M:%S", time.gmtime(t))+ "Total images processed = {0}, detected = {1}".format(l, tt))
    else:
        # log error the message 
        g_logObj.warn("Unable to delete files")
    await asyncio.sleep(dummySleep)
    return True


# ============================ process Experiment Images Message ============================ #
async def processExperimentImages(msgBody):
    global g_logObj
    g_logObj.info("Process Experiment Message Received ... {} {} {}".format( msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID], 
                                                                        msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
                                                                        msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_OFFSET_POSITION ]))
    objProc = docker_clsOpenCVProcessImages.clsOpenCVProcessImages()
    objProc.set_MessageId(msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID])
    objProc.set_verbosity(False)
    l, tt, t  = objProc.processImages(      offset = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_OFFSET_POSITION ], 
                                            imageSrcFolder = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_SRC_IMG_FOLDER ],  
                                            imageDestinationFolder = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_DEST_FOLDER ],
                                            experimentName = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
                                            imageBatchSize = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_BATCH_SIZE ],
                                            partOfFileName=  msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_PART_OF_FILE_NAME ])
    g_logObj.info("... Processed Images {} {} {}".format( msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID],
                                                        msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
                                                        msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_OFFSET_POSITION ]))
    g_logObj.info("...Elapsed time = " + time.strftime("%H:%M:%S", time.gmtime(t))+ "; Total images processed = {0}, detected = {1}".format(l, tt))   
    await asyncio.sleep(dummySleep)
    return True

# ============================ Image Processors ============================ #
#TODO:: Make this more sanitised 
async def commonDetectorProcessing(msgBody, detectorType, callBackfn):
    global g_logObj
    brv  = False
    g_logObj.info("{} Detector Message Received ... {} {}".format(   detectorType, 
                                                                        msgBody[common._MESSAGE_TYPE_DETECTOR_MESSAGE_ID], 
                                                                        msgBody[common._MESSAGE_TYPE_DETECTOR_CREATION_DATE_TIME ]))
    if (msgBody[common._MESSAGE_TYPE_DETECTOR_EXPERIMENT_NAME ] is None):
        g_logObj.info("...{} Detector, Dummy message received".format(detectorType))
        brv = True
    else:                                                              
        brv = callBackfn(msgBody)
    await asyncio.sleep(dummySleep)
    g_logObj.info("...{} Detector".format(detectorType))
    return brv

async def processImagesUsingGoogleDetector(msgBody):
    # global g_logObj
    # brv = True
    # g_logObj.info("processImagesUsingGoogleDetector ...")
    return await commonDetectorProcessing(msgBody, "google", GoogleDetector)
    # if (dmsg):
    #     pass
    # else:
    #     brv = GoogleDetector(msgBody)
    # await asyncio.sleep(dummySleep)
    # return brv

def GoogleDetector(msgBody):
    global g_logObj
    g_logObj.info("GoogleDetector ...")
    from googleImageDetector import processImages as googleTest
    googleTest(experimentName = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
                messageId = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID])
    return True

async def processImagesUsingAzureDetector(msgBody):
    return await commonDetectorProcessing(msgBody, "Azure", AzureDetector)
    # global g_logObj
    # brv = True
    # g_logObj.info("processImagesUsingAzureDetector ...")
    # dmsg = commonDetectorProcessing(msgBody, "Azure")
    # if (dmsg):
    #     pass
    # else:
    #     brv = AzureDetector(msgBody)
    # await asyncio.sleep(dummySleep)
    # return brv

def AzureDetector(msgBody):
    global g_logObj
    g_logObj.info("AzureDetector ...")
    return True

async def processImagesUsingMobileNetDetector(msgBody):
    return await commonDetectorProcessing(msgBody, "Mobile Net", MobileNetDetector)
    # global g_logObj
    # brv = True
    # g_logObj.info("processImagesUsingMobileNetDetector ...")
    # dmsg = commonDetectorProcessing(msgBody, "Mobile Net Detector")
    # if (dmsg):
    #     pass
    # else:
    #     brv = MobileNetDetector(msgBody)
    # await asyncio.sleep(dummySleep)
    # return brv

def MobileNetDetector(msgBody):
    global g_logObj
    g_logObj.info("MobileNetDetector ...")
    from mobileNetImageDetector import processImages as mobileTest
    mobileTest(experimentName = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
                messageId = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID])
    return True

async def processImagesUsingYoloDetector(msgBody):
    return await commonDetectorProcessing(msgBody, "Yolo", YoloDetector)
    # global g_logObj
    # brv = True
    # g_logObj.info("processImagesUsingYoloDetector ...")
    # dmsg = commonDetectorProcessing(msgBody, "Yolo Detector")
    # if (dmsg):
    #     pass
    # else:
    #     brv = YoloDetector(msgBody)
    # await asyncio.sleep(dummySleep)
    # return brv


def YoloDetector(msgBody):
    global g_logObj
    g_logObj.info("YoloDetector ...")
    from yoloBirdImageDetector import processImages as yoloTest
    yoloTest(   experimentName = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
                messageId = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID])
    return True

async def processImagesUsingTenslorFlowDetector(msgBody):
    return await commonDetectorProcessing(msgBody, "TensorFlow", TenslorFlowDetector)
    # global g_logObj
    # brv = True
    # g_logObj.info("processImagesUsingTenslorFlowDetector ...")
    # dmsg = commonDetectorProcessing(msgBody, "Tensor Detector")
    # if (dmsg):
    #     pass
    # else:
    #     brv = TenslorFlowDetector(msgBody)
    # await asyncio.sleep(dummySleep)
    # return brv

def TenslorFlowDetector(msgBody):
    global g_logObj
    g_logObj.info("TenslorFlowDetector ...")
    return True




