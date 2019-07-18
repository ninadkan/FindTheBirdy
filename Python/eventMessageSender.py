from azure.eventhub import EventHubClient, Sender, EventData, EventHubClientAsync, AsyncReceiver
import json
import os
import datetime
import common
from itertools import cycle
import asyncioBase
import asyncio
import time

ADDRESS = os.environ.get('EVENT_HUB_ADDRESS')
USER = os.environ.get('EVENT_HUB_SENDER_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SENDER_SAS_KEY')

import logging
from loggingBase import getGlobalHandler, getGlobalLogObject, clsLoggingBase
g_logObj = getGlobalLogObject(__name__)

def _getStartExperimentMessagePayload(experimentName):
    import uuid
    messageId = uuid.uuid4()
    currentDate = datetime.datetime.now()
    r = json.dumps({common._MESSAGE_TYPE_TAG: common._MESSAGE_TYPE_START_EXPERIMENT, \
                    common._MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID: str(messageId), \
                    common._MESSAGE_TYPE_START_EXPERIMENT_EXPERIMENT_NAME: experimentName, \
                    common._MESSAGE_TYPE_START_EXPERIMENT_CREATION_DATE_TIME: currentDate.strftime("%c")} )
    return r, str(messageId)

def _getProcessExperimentPayload(   MessageId,
                                    experimentName, 
                                    srcImageFolder,
                                    destinationFolder,
                                    imageBatchSize, 
                                    offsetPosition,
                                    partOfFileName):
    r = json.dumps({common._MESSAGE_TYPE_TAG: common._MESSAGE_TYPE_PROCESS_EXPERIMENT, \
                    common._MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID : MessageId,
                    common._MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME : experimentName, 
                    common._MESSAGE_TYPE_PROCESS_EXPERIMENT_CREATION_DATE_TIME : datetime.datetime.now().strftime("%c"),
                    common._MESSAGE_TYPE_PROCESS_EXPERIMENT_SRC_IMG_FOLDER : srcImageFolder,
                    common._MESSAGE_TYPE_PROCESS_EXPERIMENT_DEST_FOLDER : destinationFolder,
                    common._MESSAGE_TYPE_PROCESS_EXPERIMENT_BATCH_SIZE :imageBatchSize,
                    common._MESSAGE_TYPE_PROCESS_EXPERIMENT_OFFSET_POSITION :offsetPosition,
                    common._MESSAGE_TYPE_PROCESS_EXPERIMENT_PART_OF_FILE_NAME:partOfFileName} )
    return r, str(MessageId)


detectorsTypes = {  common._MESSAGE_CONSUMER_GRP_GOOGLE:common._MESSAGE_TYPE_DETECTOR_GOOGLE, 
                    common._MESSAGE_CONSUMER_GRP_AZURE:common._MESSAGE_TYPE_DETECTOR_AZURE, 
                    common._MESSAGE_CONSUMER_GRP_YOLO:common._MESSAGE_TYPE_DETECTOR_YOLO, 
                    common._MESSAGE_CONSUMER_GRP_MOBILENET:common._MESSAGE_TYPE_DETECTOR_MOBILE_NET, 
                    common._MESSAGE_CONSUMER_GRP_TENSORFLOW:common._MESSAGE_TYPE_DETECTOR_TENSORFLOW}

def _getDetectorTypeMessagePayload(MessageId, experimentName, destinationFolder, detector ):
    r = json.dumps({common._MESSAGE_TYPE_TAG: detector, 
                    common._MESSAGE_TYPE_DETECTOR_MESSAGE_ID : MessageId,
                    common._MESSAGE_TYPE_DETECTOR_EXPERIMENT_NAME : experimentName, 
                    common._MESSAGE_TYPE_DETECTOR_CREATION_DATE_TIME : datetime.datetime.now().strftime("%c"),
                    common._MESSAGE_TYPE_DETECTOR_DEST_FOLDER : destinationFolder} )
    return r, str(MessageId)    



async def sendMessageAsync(payload, partition="0"):
    global g_logObj
    g_logObj.debug("sendMessageAsync")
    
    client = EventHubClientAsync(ADDRESS, debug=True, username=USER, password=KEY) 
    sender = client.add_async_sender(partition=partition)
    await client.run_async()
    data = EventData(payload)
    await sender.send(data)
    await client.stop_async()
    print('message sent {}'.format(payload))
                              

async def sendStartExperimentMessage(experimentNames):
    global ADDRESS
    global USER
    global KEY
    global g_logObj
    g_logObj.debug("sendStartExperimentMessage")
    
    if not ADDRESS:
        raise ValueError("No EventHubs URL supplied.") 
    
    
    lstGuids = []
    for experimentName in experimentNames:
        r, guid = _getStartExperimentMessagePayload(experimentName)
        lstGuids.append(json.dumps({experimentName:guid}))
        try:
            await sendMessageAsync(r, "0") 
        except Exception as e:
            raise
    return   lstGuids      


pool = cycle(["0", "1","2","3"]) #picking the partition where the messages will be processed 

async def sendProcessExperimentMessage(   MessageId,
                                    experimentName, 
                                    srcImageFolder,
                                    destinationFolder,
                                    imageBatchSize, 
                                    pos,
                                    partOfFileName):
    global ADDRESS
    global USER
    global KEY
    global pool
    global g_logObj
    g_logObj.debug("sendProcessExperimentMessage")
    guid = None

    if not ADDRESS:
        raise ValueError("No EventHubs URL supplied.")                                    

    try:
        payload, guid = _getProcessExperimentPayload( MessageId,
                                                experimentName, 
                                                srcImageFolder,
                                                destinationFolder,
                                                imageBatchSize, 
                                                pos,
                                                partOfFileName)

        await sendMessageAsync(payload, next(pool)) 
    except Exception as e:
        raise
    finally:
        pass
    return   guid                                  


async def sendDetectorMessages(MessageId,experimentName,destinationFolder):
    global ADDRESS
    global USER
    global KEY
    global pool
    global g_logObj
    g_logObj.debug("sendDetectorMessages")
    guid = None

    if not ADDRESS:
        raise ValueError("No EventHubs URL supplied.")                                    
    lstGuids = []
    for key, value in detectorsTypes.items():
        r, guid = _getDetectorTypeMessagePayload(MessageId, experimentName, destinationFolder, value )
        lstGuids.append(json.dumps({experimentName:guid}))
        try:
            await sendMessageAsync(r, "0") # we need only one instance of these detectors running! 
        except Exception as e:
            raise
        finally:
            pass
    return   lstGuids      
