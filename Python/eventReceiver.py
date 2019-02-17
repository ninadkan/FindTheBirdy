# https://github.com/Azure/azure-event-hubs-python
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


"""
An example to show receiving events from an Event Hub partition.
"""
import os
import sys
import logging
import time
from azure.eventhub import EventHubClient, Receiver, Offset, EventHubClientAsync, AsyncReceiver
import json
import argparse
import requests
import common
# import openCVPhotoExtractorTest as test
# import openCVPhotoExtractorClsImpl as clsImpl

import signal
import functools

import eventMessageProcessor
import cosmosDB.cosmosImageOperations
import loggingBase 
import asyncio

# mapper of eventMessage Type and function which processes it
dispatch={
    common._MESSAGE_TYPE_PROCESS_EXPERIMENT:eventMessageProcessor.processExperimentImages,
    common._MESSAGE_TYPE_START_EXPERIMENT:eventMessageProcessor.processStartExperimentMessage,
    common._MESSAGE_TYPE_DETECTOR_GOOGLE:eventMessageProcessor.processImagesUsingGoogleDetector,
    common._MESSAGE_TYPE_DETECTOR_AZURE:eventMessageProcessor.processImagesUsingAzureDetector,
    common._MESSAGE_TYPE_DETECTOR_YOLO:eventMessageProcessor.processImagesUsingYoloDetector,
    common._MESSAGE_TYPE_DETECTOR_MOBILE_NET:eventMessageProcessor.processImagesUsingMobileNetDetector,
    common._MESSAGE_TYPE_DETECTOR_TENSORFLOW:eventMessageProcessor.processImagesUsingTenslorFlowDetector
}

async def processMessages(client, partition, consumerGrp, logger):
    start_time = time.time()
    total = 0
    cleanUp = False
    last_sn = -1
    last_offset = "-1"

    msgOperations = cosmosDB.cosmosImageOperations.clsCosmosImageProcessingOperations()
    last_offset_value = msgOperations.get_offsetValue(EVENTHUB, partition, consumerGrp, msgType)
    
    # OFFSET = Offset(returnValue['result']) # returns -1 if no previous one are found. 
    # receiver = client.add_receiver(consumerGrp, partition, prefetch=5000, offset=Offset(last_offset_value))
    receiver = client.add_async_receiver(consumerGrp, partition, prefetch=5000, offset=Offset(last_offset_value))
    #client.run()
    await client.run_async()
    
    #batch = receiver.receive(timeout=60*5)
    receiver_timeOut = 5

    timeout = time.time() + 60*6 # six minutes from now
    statusUpdate = cosmosDB.cosmosStatusUpdate.clsStatusUpdate() 
    while (time.time() < timeout):
        
        batch = await receiver.receive(timeout=receiver_timeOut)
        if (batch):
            logger.warning('{} : starting batch time ...{}'.format(consumerGrp, time.strftime("%H:%M:%S", time.localtime())))
            for event_data in batch:
                last_offset = event_data.offset
                last_sn = event_data.sequence_number

                logger.warning('{} :Number of messages in the batch {}'.format(consumerGrp, len(batch)))
                #logger.error("Received: {}, {}".format(last_offset.value, last_sn))
                brv, loaded_r = common.is_json(event_data.body_as_str())
                if (brv == True):

                    # each message has an indicator of what type it is; That defines our eventReceiver Type
                    if (loaded_r[common._MESSAGE_TYPE_TAG]== msgType):
                        total =+1
                        if (dispatch[loaded_r[common._MESSAGE_TYPE_TAG]]):
                            logger.warning(loaded_r[common._MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID])
                            brv = True if cleanUp else await dispatch[loaded_r[common._MESSAGE_TYPE_TAG]](loaded_r, logger)
                            if (brv == True):
                                brv = msgOperations.insert_offset_document( EVENTHUB, 
                                                                            partition, 
                                                                            consumerGrp,
                                                                            last_offset.value, 
                                                                            loaded_r[common._MESSAGE_TYPE_TAG])
                        else:
                            logger.error("Unknown Message!!!  {}".format(msgBody))
                            continue
                    else:
                        # nothing to do with us, ignore and continue
                        logger.warning('{} :Incompatible message type received, ignoring'.format(consumerGrp,loaded_r[common._MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID]))
                        if (cleanUp== True):
                            msgOperations.insert_offset_document(EVENTHUB, partition, consumerGrp,last_offset.value, msgType)
                        continue
                else:
                    logger.error('Message body is not json! {}'.format(event_data.body_as_str()))
                    continue
                
                timeout = time.time() + 60*5 # reset our timer
                logger.warning('{} : checkout time increased ...{}'.format(consumerGrp, time.strftime("%H:%M:%S", time.localtime())))
    end_time = time.time()
    await client.stop_async()
    run_time = end_time - start_time
    print("{} : Received {} messages in {} seconds".format(consumerGrp, total, run_time))

try:

    ADDRESS = os.environ.get('EVENT_HUB_ADDRESS')
    USER = os.environ.get('EVENT_HUB_RECEIVER_SAS_POLICY')
    KEY = os.environ.get('EVENT_HUB_RECEIVER_SAS_KEY')
    EVENTHUB = os.environ.get('EVENT_HUB_NAME')

    logger = loggingBase.get_logger(logging.WARNING)
    logger.warning("creating event hub class")

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--partition", help="partition", type=int, default=0)
    parser.add_argument("-c", "--consumergrp", help="Consumer Group", type=str, default='opencv')
    args = parser.parse_args()
    logger.warning(args.partition)
    consumerGroup = args.consumergrp
    logger.warning(consumerGroup)

    msgType = None
    msgType = common._ConsumerGrp_MessageType_Mapping[consumerGroup]

    if (msgType is None): 
       raise ValueError('unknown message type specified {}'.format(consumerGroup))

    loop = asyncio.get_event_loop()
    client = EventHubClientAsync(ADDRESS, debug=True, username=USER, password=KEY)
    tasks = [asyncio.ensure_future(processMessages(client, args.partition, consumerGroup, logger ))]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
except KeyboardInterrupt:
    pass
finally:
    #loop.run_until_complete(client.stop_async())
    pass

