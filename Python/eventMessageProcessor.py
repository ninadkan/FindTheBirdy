

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



async def processMessageBody(context, messages, consumerGrp, logger=None):
    brv = False
    try:
        for message in messages:
            msgBody =  message.body_as_str()
            brv, loaded_r = is_json(message.body_as_str())
            if (brv == True):
                if (loaded_r[common._MESSAGE_TYPE_TAG]== common._MESSAGE_TYPE_START_EXPERIMENT):
                    if(consumerGrp == common._MESSAGE_CONSUMER_GRP_STARTEXPERIMENT):
                        logger.warning(loaded_r)
                        brv = await processStartExperimentMessage(loaded_r, logger)
                        if (brv == True):
                            await context.checkpoint_async()
                elif (loaded_r[common._MESSAGE_TYPE_TAG]== common._MESSAGE_TYPE_PROCESS_EXPERIMENT):
                    if (consumerGrp == common._MESSAGE_CONSUMER_GRP_OPENCV):
                        logger.warning(loaded_r)
                        brv = processExperimentImages(loaded_r, logger)
                        if (brv == True):
                            await context.checkpoint_async()
                else:
                    logger.warning("Unknown, non-compatible message!!!  {}".format(msgBody))
            else:
                logger.warning(" Message is not JSON!!!  {}".format(msgBody))
            if (brv == False):
                break

        # if (brv == True):
        #     logger.warning("Events processed {}".format(context.sequence_number))
        #     # remember that the checkpoint is after a batch has been delivered;
        #     # not after every message
        #     await context.checkpoint_async()
        # else:
        #     logger.error("Error Processing Messages !!!")
    except Exception as e:
        # check pointing any way
        logger.error("Error Processing Messages in !!!" + message.body_as_str())
        logger.error("Internal error {} {}".format(e.message, e.args))
    return brv

def is_json(msgBody):
    json_object = None
    try:
        json_object = json.loads(msgBody)
    except Exception as e:
        return False, json_object
    return True, json_object


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

def processExperimentImages(msgBody, logger):
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
    return True




