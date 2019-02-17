

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



# async def processMessageBody(context, messages, consumerGrp, logger=None):
#     brv = False
#     try:
#         for message in messages:
#             msgBody =  message.body_as_str()
#             brv, loaded_r = common.is_json(message.body_as_str())
#             if (brv == True):
#                 if (loaded_r[common._MESSAGE_TYPE_TAG]== common._MESSAGE_TYPE_START_EXPERIMENT):
#                     if(consumerGrp == common._MESSAGE_CONSUMER_GRP_STARTEXPERIMENT):
#                         #logger.warning(loaded_r)
#                         brv = await processStartExperimentMessage(loaded_r, logger)
#                         if (brv == True):
#                             await context.checkpoint_async()
#                 elif (loaded_r[common._MESSAGE_TYPE_TAG]== common._MESSAGE_TYPE_PROCESS_EXPERIMENT):
#                     if (consumerGrp == common._MESSAGE_CONSUMER_GRP_OPENCV):
#                         #logger.warning(loaded_r)
#                         brv = processExperimentImages(loaded_r, logger)
#                         if (brv == True):
#                             await context.checkpoint_async()
#                 else:
#                     logger.warning("Unknown, non-compatible message!!!  {}".format(msgBody))
#             else:
#                 logger.warning(" Message is not JSON!!!  {}".format(msgBody))
#             if (brv == False):
#                 break

#         # if (brv == True):
#         #     logger.warning("Events processed {}".format(context.sequence_number))
#         #     # remember that the checkpoint is after a batch has been delivered;
#         #     # not after every message
#         #     await context.checkpoint_async()
#         # else:
#         #     logger.error("Error Processing Messages !!!")
#     except Exception as e:
#         # check pointing any way
#         logger.error("Error Processing Messages in !!!" + message.body_as_str())
#         logger.error("Internal error {} {}".format(e.message, e.args))
#     return brv

async def processStartExperimentMessage(msgBody, logger):
    brv = False
    experimentName = msgBody[common._MESSAGE_TYPE_START_EXPERIMENT_EXPERIMENT_NAME]
    assert(experimentName is not None), "No experiment name passed!"
    brv = test.delete_existing_files(experimentName)
    if (brv == True):
        # send messages to start processing the images,
        procObject = openCVPhotoExtractorClsImpl.clsOpenCVObjectDetector(experimentName=experimentName)
        procObject.set_MessageId(msgBody[common._MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID])
        #l, tt,  t = procObject.processImages(partOfFileName='2018-12-14_04')
        
        l, tt,  t = await procObject.processImages()
        logger.warn ("Return from processStartExperimentMessage!!!")
        logger.warn("Elapsed time = " + time.strftime("%H:%M:%S", time.gmtime(t))+ "Total images processed = {0}, detected = {1}".format(l, tt))
    else:
        # log error the message 
        logger.warn("Unable to delete files")
    return True

dummySleep=1

async def processExperimentImages(msgBody, logger):
    logger.warn("Process Experiment Message Received ... {} {}".format( msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID], 
                                                                        msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
                                                                        msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_OFFSET_POSITION ]))
    objProc = docker_clsOpenCVProcessImages.clsOpenCVProcessImages()
    objProc.set_MessageId(msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID])
    objProc.set_verbosity(False)
    l, tt, t  = objProc.processImages(  offset = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_OFFSET_POSITION ], 
                            imageSrcFolder = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_SRC_IMG_FOLDER ],  
                            imageDestinationFolder = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_DEST_FOLDER ],
                            experimentName = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
                            imageBatchSize = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_BATCH_SIZE ],
                            partOfFileName=  msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_PART_OF_FILE_NAME ])
    logger.warn("... Processed Images {} {} {}".format( msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID],
                                                        msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
                                                        msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_OFFSET_POSITION ]))
    logger.warn("...Elapsed time = " + time.strftime("%H:%M:%S", time.gmtime(t))+ "; Total images processed = {0}, detected = {1}".format(l, tt))   
    await asyncio.sleep(dummySleep)
    return True

async def processImagesUsingGoogleDetector(msgBody, logger):
    #export GOOGLE_APPLICATION_CREDENTIALS=<path_to_service_account_file>
    from googleImageDetector import processImages as googleTest
    logger.warning("Google Detector")
    googleTest(experimentName = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
                messageId = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID])
    await asyncio.sleep(dummySleep)
    return True


async def processImagesUsingAzureDetector(msgBody, logger):
    # from azureImageDetector import processImages as azureTest, verbosity as azureVerbosity
    # Detector = "Azure Detector"
    # print(Detector)
    # azureTest(experimentName = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
    #            messageId = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID])
    await asyncio.sleep(dummySleep)
    return True

async def processImagesUsingMobileNetDetector(msgBody, logger):
    # Run the tests now
    from mobileNetImageDetector import processImages as mobileTest
    logger.warning("Mobile Net Detector")
    mobileTest(experimentName = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
                messageId = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID])
    await asyncio.sleep(dummySleep)
    return True


async def processImagesUsingYoloDetector(msgBody, logger):
    from yoloBirdImageDetector import processImages as yoloTest
    logger.warning("Yolo Detector")
    yoloTest(   experimentName = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
                messageId = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID])
    await asyncio.sleep(dummySleep)
    return True

async def processImagesUsingTenslorFlowDetector(msgBody, logger):
    await asyncio.sleep(dummySleep)
    return True




