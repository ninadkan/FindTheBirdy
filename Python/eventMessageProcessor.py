

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
import openCVPhotoExtractorClsImpl as clsImpl
import docker_clsOpenCVProcessImages as ds



async def processMessageBody(context, messages, logger=None):
    brv = False
    for message in messages:
        msgBody =  message.body_as_str()
        print(msgBody)
        brv, loaded_r = is_json(message.body_as_str())
        if (brv == True):
            if (loaded_r[common._MESSAGE_TYPE_TAG]== common._MESSAGE_TYPE_START_EXPERIMENT):
                brv = await processStartExperimentMessage(loaded_r, logger)
            elif (loaded_r[common._MESSAGE_TYPE_TAG]== common._MESSAGE_TYPE_EXPERIMENT_ATTRIBUTES):
                brv = await processExperimentImages(loaded_r, logger)
            else:
                print("Unknown Message!!!  {}".format(msgBody))
        else:
            print("Unknown Message!!!  {}".format(msgBody))
        if (brv == False):
            break

    if (brv == True):
        print("Events processed {}".format(context.sequence_number))
        # remember that the checkpoint is after a batch has been delivered;
        # not after every message
        await context.checkpoint_async()
    else:
        logger.error("Error Processing Messages !!!")
    return brv

def is_json(msgBody):
    json_object = None
    try:
        json_object = json.loads(msgBody)
    except Exception as e:
        return False, json_object
    return True, json_object


async def processStartExperimentMessage(msgBody, logger=None):
    brv = False
    experimentName = msgBody[common._MESSAGE_TYPE_START_EXPERIMENT_EXPERIMENT_NAME]
    assert(experimentName is not None), "No experiment name passed!"
    brv = test.delete_existing_files(experimentName)
    if (brv == True):
        # send messages to start processing the images, challenge is the message guid is getting lost
        procObject = clsImpl.clsOpenCVObjectDetector(experimentName=experimentName)
        procObject.set_MessageId(msgBody[common._MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID])
        #l, tt,  t = procObject.processImages(partOfFileName='2018-12-14_04')
        l, tt,  t = procObject.processImages()
        brv = updateNewOffset(partition, last_offset)
        print ("")
        print("Elapsed time = " + time.strftime("%H:%M:%S", time.gmtime(t))+ "Total images processed = {0}, detected = {1}".format(l, tt))
    else:
        # log error the message 
        logger.warn("Unable to delete files")
    return brv

async def processExperimentImages(msgBody, logger=None):
    print("Process Experiment Message Received ... {} {}".format( msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID], 
                                                                        msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
                                                                        msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_OFFSET_POSITION ]))
    objProc = ds.clsOpenCVProcessImages()
    objProc.set_verbosity(False)
    objProc.processImages(  offset = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_OFFSET_POSITION ], 
                            imageSrcFolder = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_SRC_IMG_FOLDER ],  
                            imageDestinationFolder = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_DEST_FOLDER ],
                            experimentName = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
                            imageBatchSize = msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_BATCH_SIZE ],
                            partOfFileName=  msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_PART_OF_FILE_NAME ])
    print("... Processed Images {} {} {}".format( msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID],
                                                        msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME ],
                                                        msgBody[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_OFFSET_POSITION ]))
    return 




