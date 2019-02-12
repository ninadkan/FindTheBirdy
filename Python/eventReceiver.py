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
    batch = await receiver.receive(timeout=60*5)
    while batch:
        logger.warning('starting batch time ...{}'.format(time.strftime("%H:%M:%S", time.localtime())))
        for event_data in batch:
            last_offset = event_data.offset
            last_sn = event_data.sequence_number

            logger.warning('Number of messages in the batch {}'.format(len(batch)))
            
            #logger.error("Received: {}, {}".format(last_offset.value, last_sn))
            brv, loaded_r = eventMessageProcessor.is_json(event_data.body_as_str())
            if (brv == True):
                if (loaded_r[common._MESSAGE_TYPE_TAG]== msgType):
                    total =+1
                    if (loaded_r[common._MESSAGE_TYPE_TAG]== common._MESSAGE_TYPE_START_EXPERIMENT):
                        logger.warning(loaded_r[common._MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID])
                        brv = True if cleanUp else await eventMessageProcessor.processStartExperimentMessage(loaded_r, logger)
                        if (brv == True):
                            brv = msgOperations.insert_offset_document(EVENTHUB, partition, consumerGrp,last_offset.value, common._MESSAGE_TYPE_START_EXPERIMENT)
                    elif (loaded_r[common._MESSAGE_TYPE_TAG]== common._MESSAGE_TYPE_PROCESS_EXPERIMENT):
                        logger.warning(loaded_r[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID])
                        brv = True if cleanUp else eventMessageProcessor.processExperimentImages(loaded_r, logger)
                        if (brv == True):
                            brv = msgOperations.insert_offset_document(EVENTHUB, partition, consumerGrp,last_offset.value, common._MESSAGE_TYPE_PROCESS_EXPERIMENT)
                    else:
                        logger.error("Unknown Message!!!  {}".format(msgBody))
                        continue
                else:
                    # nothing to do with us, ignore and continue
                    logger.warning('Incompatible message type received, ignoring'.format(loaded_r[common._MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID]))
                    if (cleanUp== True):
                        msgOperations.insert_offset_document(EVENTHUB, partition, consumerGrp,last_offset.value, msgType)
                    continue
            else:
                logger.error('Message body is not json! {}'.format(event_data.body_as_str()))
                continue
        logger.warning('checking another receive....{}'.format(time.strftime("%H:%M:%S", time.localtime())))
        #batch = receiver.receive(timeout=5)
        batch = await receiver.receive(timeout=60)
    end_time = time.time()
    await client.stop_async()
    run_time = end_time - start_time
    print("Received {} messages in {} seconds".format(total, run_time))

try:

    ADDRESS = os.environ.get('EVENT_HUB_ADDRESS')
    USER = os.environ.get('EVENT_HUB_RECEIVER_SAS_POLICY')
    KEY = os.environ.get('EVENT_HUB_RECEIVER_SAS_KEY')
    CONSUMER_GROUP = os.environ.get('EVENT_HUB_RECEIVER_CONSUMER_GRP') #"opencv" #$default"
    EVENTHUB = os.environ.get('EVENT_HUB_NAME')

    logger = loggingBase.get_logger(logging.WARNING)
    logger.warning("creating event hub class")

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--partition", help="partition", type=int, default=0)
    args = parser.parse_args()
    logger.warning(args.partition)
    logger.warning(CONSUMER_GROUP)

    if(CONSUMER_GROUP == common._MESSAGE_CONSUMER_GRP_OPENCV):
        msgType = common._MESSAGE_TYPE_PROCESS_EXPERIMENT
    elif (CONSUMER_GROUP == common._MESSAGE_CONSUMER_GRP_STARTEXPERIMENT):
        msgType = common._MESSAGE_TYPE_START_EXPERIMENT
    else:
        raise ValueError('unknown message type specified {}'.format(CONSUMER_GROUP))

    loop = asyncio.get_event_loop()
    #client = EventHubClient(ADDRESS, debug=True, username=USER, password=KEY)
    client = EventHubClientAsync(ADDRESS, debug=True, username=USER, password=KEY)
    tasks = [asyncio.ensure_future(processMessages(client, args.partition, CONSUMER_GROUP, logger ))]
    loop.run_until_complete(asyncio.wait(tasks))
    #loop.run_until_complete(client.stop_async())
    loop.close()
except KeyboardInterrupt:
    pass
finally:
    #loop.run_until_complete(client.stop_async())
    pass

