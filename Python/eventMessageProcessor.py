

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
    return True


# ============================ process Experiment Images Message ============================ #
dummySleep=1

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
async def commonProcessImageDetector(msgBody, detectorType, callBackfn):
    global g_logObj
    brv = False
    g_logObj.info("{} Detector Message Received ... {} {} {}".format(   detectorType, 
                                                                        msgBody[common._MESSAGE_TYPE_DETECTOR_MESSAGE_ID], 
                                                                        msgBody[common._MESSAGE_TYPE_DETECTOR_EXPERIMENT_NAME ],
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
    return commonProcessImageDetector(msgBody, "google" , GoogleDetector)
    # global g_logObj
    # g_logObj.info("Google Detector Message Received ... {} {} {}".format( msgBody[common._MESSAGE_TYPE_DETECTOR_MESSAGE_ID], 
    #                                                                     msgBody[common._MESSAGE_TYPE_DETECTOR_EXPERIMENT_NAME ],
    #                                                                     msgBody[common._MESSAGE_TYPE_DETECTOR_CREATION_DATE_TIME ]))    
    # from googleImageDetector import processImages as googleTest
    # googleTest(experimentName = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
    #             messageId = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID])
    # await asyncio.sleep(dummySleep)
    # g_logObj.info("...Google Detector")
    # return True

async def GoogleDetector(msgBody):
    from googleImageDetector import processImages as googleTest
    googleTest(experimentName = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
                messageId = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID])
    return True


async def processImagesUsingAzureDetector(msgBody):
    return commonProcessImageDetector(msgBody, "Azure" , AzureDetector  )
    # global g_logObj
    # g_logObj.info("Azure Detector Message Received ... {} {} {}".format( msgBody[common._MESSAGE_TYPE_DETECTOR_MESSAGE_ID], 
    #                                                                 msgBody[common._MESSAGE_TYPE_DETECTOR_EXPERIMENT_NAME ],
    #                                                                 msgBody[common._MESSAGE_TYPE_DETECTOR_CREATION_DATE_TIME ]))    
    # from azureImageDetector import processImages as azureTest, verbosity as azureVerbosity
    # Detector = "Azure Detector"
    # print(Detector)
    # azureTest(experimentName = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
    #            messageId = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID])
    # await asyncio.sleep(dummySleep)
    # g_logObj.info("...Azure Detector")
    # return True

async def AzureDetector(msgBody):
    return True

async def processImagesUsingMobileNetDetector(msgBody):
    return commonProcessImageDetector(msgBody, "Mobile Net Detector" , MobileNetDetector )
    # g_logObj.info("Mobile Net Detector")
    # g_logObj.info("Mobile Detector Message Received ... {} {} {}".format( msgBody[common._MESSAGE_TYPE_DETECTOR_MESSAGE_ID], 
    #                                                                 msgBody[common._MESSAGE_TYPE_DETECTOR_EXPERIMENT_NAME ],
    #                                                                 msgBody[common._MESSAGE_TYPE_DETECTOR_CREATION_DATE_TIME ]))    
    # # Run the tests now
    # from mobileNetImageDetector import processImages as mobileTest
    # g_logObj.info("Mobile Net Detector")
    # mobileTest(experimentName = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
    #             messageId = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID])
    # await asyncio.sleep(dummySleep)
    # g_logObj.info("...Mobile Detector")

    # return True

async def MobileNetDetector(msgBody):
    from mobileNetImageDetector import processImages as mobileTest
    mobileTest(experimentName = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
                messageId = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID])
    return True
  



async def processImagesUsingYoloDetector(msgBody):
    return commonProcessImageDetector(msgBody, "Yolo Detector" , YoloDetector )
    # g_logObj.info("Yolo Detector Message Received ... {} {} {}".format( msgBody[common._MESSAGE_TYPE_DETECTOR_MESSAGE_ID], 
    #                                                                 msgBody[common._MESSAGE_TYPE_DETECTOR_EXPERIMENT_NAME ],
    #                                                                 msgBody[common._MESSAGE_TYPE_DETECTOR_CREATION_DATE_TIME ]))    
    # from yoloBirdImageDetector import processImages as yoloTest
    # g_logObj.info("Yolo Detector")
    # yoloTest(   experimentName = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
    #             messageId = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID])
    # await asyncio.sleep(dummySleep)
    # g_logObj.info("...Yolo Detector")    
    # return True

async def YoloDetector(msgBody):
    from yoloBirdImageDetector import processImages as yoloTest
    yoloTest(   experimentName = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
                messageId = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID])
    return True


async def processImagesUsingTenslorFlowDetector(msgBody):
    return commonProcessImageDetector(msgBody, "Tensor Flow Detector" , TenslorFlowDetector )
    # g_logObj.info("Tensorflow Detector Message Received ... {} {} {}".format( msgBody[common._MESSAGE_TYPE_DETECTOR_MESSAGE_ID], 
    #                                                             msgBody[common._MESSAGE_TYPE_DETECTOR_EXPERIMENT_NAME ],
    #                                                             msgBody[common._MESSAGE_TYPE_DETECTOR_CREATION_DATE_TIME ]))    
    # await asyncio.sleep(dummySleep)
    # g_logObj.info("...Tensorflow Detector")        
    # return True

async def TenslorFlowDetector(msgBody):
    return True




