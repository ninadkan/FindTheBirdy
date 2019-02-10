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
from azure.eventhub import EventHubClient, Receiver, Offset
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

# resp = requests.get('https://todolist.example.com/tasks/')
# if resp.status_code != 200:
#     # This means something went wrong.
#     raise ApiError('GET /tasks/ {}'.format(resp.status_code))
# for todo_item in resp.json():
#     print('{} {}'.format(todo_item['id'], todo_item['summary']))


# task = {"summary": "Take out trash", "description": "" }
# resp = requests.post('https://todolist.example.com/tasks/', json=task)
# if resp.status_code != 201:
#     raise ApiError('POST /tasks/ {}'.format(resp.status_code))
# print('Created task. ID: {}'.format(resp.json()["id"]))


# # The shortcut
# resp = requests.post('https://todolist.example.com/tasks/', json=task)
# # The equivalent longer version
# resp = requests.post('https://todolist.example.com/tasks/',
#                      data=json.dumps(task),
#                      headers={'Content-Type':'application/json'},


# def is_json(myjson):
#     json_object = None
#     try:
#         json_object = json.loads(myjson)
#     except Exception as e:
#         #print("Not json")
#         return False, json_object
#     return True, json_object




# import examples

# logger = examples.get_logger(logging.INFO)

# Address can be in either of these formats:
# "amqps://<URL-encoded-SAS-policy>:<URL-encoded-SAS-key>@<mynamespace>.servicebus.windows.net/myeventhub"
# "amqps://<mynamespace>.servicebus.windows.net/myeventhub"
ADDRESS = os.environ.get('EVENT_HUB_ADDRESS')
# SAS policy and key are not required if they are encoded in the URL
USER = os.environ.get('EVENT_HUB_RECEIVER_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_RECEIVER_SAS_KEY')
CONSUMER_GROUP = os.environ.get('EVENT_HUB_RECEIVER_CONSUMER_GRP') #"opencv" #$default"
EVENTHUB = os.environ.get('EVENT_HUB_NAME')

#OFFSET = Offset("8000")
#PARTITION = 3

last_sn = -1
last_offset = "-1"

logger = loggingBase.get_logger(logging.WARNING)
logger.warning("creating event hub class")
cleanUp = False
def processMessages():
    try:
        total = 0
        client = EventHubClient(ADDRESS, debug=True, username=USER, password=KEY)
        parser = argparse.ArgumentParser()
        parser.add_argument("--partition", help="partition", type=int, default=0)
        args = parser.parse_args()
        logger.warning(args.partition)

        logger.warning(CONSUMER_GROUP)


        if(CONSUMER_GROUP == common._MESSAGE_CONSUMER_GRP_OPENCV):
            msgType = common._MESSAGE_TYPE_PROCESS_EXPERIMENT
        elif (CONSUMER_GROUP == common._MESSAGE_CONSUMER_GRP_STARTEXPERIMENT):
            msgType = common._MESSAGE_TYPE_START_EXPERIMENT
        else:
            logger.error('unknown message type specified {}'.format(CONSUMER_GROUP))

        msgOperations = cosmosDB.cosmosImageOperations.clsCosmosImageProcessingOperations()
        last_offset_value = msgOperations.get_offsetValue(EVENTHUB, args.partition, CONSUMER_GROUP, msgType)
        
        # OFFSET = Offset(returnValue['result']) # returns -1 if no previous one are found. 
        receiver = client.add_receiver(CONSUMER_GROUP, args.partition, prefetch=5000, offset=Offset(last_offset_value))
        client.run()
        start_time = time.time()
        logger.warning('Before the starting batch ...{}'.format(time.strftime("%H:%M:%S", time.localtime())))
        batch = receiver.receive(timeout=60*5)
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
                            #logger.warning(loaded_r[common._MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID])
                            brv = True if cleanUp else eventMessageProcessor.processStartExperimentMessage(loaded_r, logger)
                            if (brv == True):
                                brv = msgOperations.insert_offset_document(EVENTHUB, args.partition, CONSUMER_GROUP,last_offset.value, common._MESSAGE_TYPE_START_EXPERIMENT)
                        elif (loaded_r[common._MESSAGE_TYPE_TAG]== common._MESSAGE_TYPE_PROCESS_EXPERIMENT):
                            #logger.warning(loaded_r[common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID])
                            brv = True if cleanUp else eventMessageProcessor.processExperimentImages(loaded_r, logger)
                            if (brv == True):
                                brv = msgOperations.insert_offset_document(EVENTHUB, args.partition, CONSUMER_GROUP,last_offset.value, common._MESSAGE_TYPE_PROCESS_EXPERIMENT)
                        else:
                            logger.error("Unknown Message!!!  {}".format(msgBody))
                            
                    else:
                        # nothing to do with us, ignore and continue
                        logger.warning('Incompatible message type received, ignoring'.format(loaded_r[common._MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID]))
                        if (cleanUp== True):
                            msgOperations.insert_offset_document(EVENTHUB, args.partition, CONSUMER_GROUP,last_offset.value, msgType)
                else:
                    logger.error('Message body is not json! {}'.format(event_data.body_as_str()))
            logger.warning('checking another receive....{}'.format(time.strftime("%H:%M:%S", time.localtime())))
            batch = receiver.receive(timeout=5)
        end_time = time.time()
        client.stop()
        run_time = end_time - start_time
        print("Received {} messages in {} seconds".format(total, run_time))

    except KeyboardInterrupt:
        pass
    finally:
        client.stop()

if __name__ == "__main__":
    processMessages()