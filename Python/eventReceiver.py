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
import openCVPhotoExtractorTest as test
import openCVPhotoExtractorClsImpl as clsImpl


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


def is_json(myjson):
    json_object = None
    try:
        json_object = json.loads(myjson)
    except Exception as e:
        #print("Not json")
        return False, json_object
    return True, json_object




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

#OFFSET = Offset("8000")
#PARTITION = 3
total = 0
last_sn = -1
last_offset = "-1"

print("creating event hub class")
client = EventHubClient(ADDRESS, debug=True, username=USER, password=KEY)


try:
    parser = argparse.ArgumentParser()
    parser.add_argument("--partition", help="partition", type=int, default=0)
    args = parser.parse_args()
    print(args.partition)

    brv, last_offset_value = getLastOffset(args.partition)
    if (brv == True):
        # OFFSET = Offset(returnValue['result']) # returns -1 if no previous one are found. 
        receiver = client.add_receiver(CONSUMER_GROUP, args.partition, prefetch=5000, offset=last_offset_value)
        client.run()
        start_time = time.time()
        batch = receiver.receive(timeout=5000)
        while batch:
            for event_data in batch:
                last_offset = event_data.offset
                last_sn = event_data.sequence_number
                
                print("Received: {}, {}".format(last_offset.value, last_sn))

                brv, loaded_r = is_json(event_data.body_as_str())
                if (brv == True):
                    if (loaded_r[common._MESSAGE_TYPE_TAG]== common._MESSAGE_TYPE_START_EXPERIMENT):
                        processStartExperimentMessage(loaded_r, args.partition, last_offset.value)
                        brv = updateNewOffset(args.partition, last_offset.value)
                    elif (loaded_r[common._MESSAGE_TYPE_TAG]== common._MESSAGE_TYPE_EXPERIMENT_ATTRIBUTES):
                        processExperimentImages(loaded_r, args.partition, last_offset.value)
                        brv = updateNewOffset(args.partition, last_offset.value)
                    else:
                        print(event_data.body_as_str())
                else:
                    print(event_data.body_as_str())
                total += 1
                # save the last offset. 
                assert(brv == True), "Error saving the new offset"
            batch = receiver.receive(timeout=5000)
        end_time = time.time()
        client.stop()
        run_time = end_time - start_time
        print("Received {} messages in {} seconds".format(total, run_time))

except KeyboardInterrupt:
    pass
finally:
    client.stop()