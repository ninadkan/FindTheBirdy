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


async def sendMessageAsync(client, payload, partition="0"):
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
    
    if not ADDRESS:
        raise ValueError("No EventHubs URL supplied.") 
    
    client = EventHubClientAsync(ADDRESS, debug=True, username=USER, password=KEY) 
    lstGuids = []
    for experimentName in experimentNames:
        r, guid = _getStartExperimentMessagePayload(experimentName)
        lstGuids.append(json.dumps({experimentName:guid}))
        

        try:
            # client = EventHubClient(ADDRESS, debug=True, username=USER, password=KEY)
            # sender = client.add_sender(partition="0") 
            # client.run()

            #loop = asyncio.get_event_loop()
            #client = EventHubClient(ADDRESS, debug=True, username=USER, password=KEY)
            #tasks = [asyncio.create_task(sendMessageAsync(client, n)) for n in lstPayloads]
            #tasks = asyncio.gather[asyncio.create_task(sendMessageAsync(client, lstPayloads[0]))]
            #start_time = time.time()
            await sendMessageAsync(client, r, "0") 
            #await client.stop_async()
            # loop.run_until_complete()
            # loop.run_until_complete()

            #end_time = time.time()
            #run_time = end_time - start_time
            #print("Runtime: {} seconds".format(run_time))
            #loop.close()                                                

            #sender = client.add_sender(partition=next(pool)) 
            #sender = client.add_sender(partition=next(pool)) 
            #client.run()
            # sender.send(EventData(r))
            #logger.info("Runtime: {} seconds".format(run_time))
        except Exception as e:
            raise
        # finally:
        #     client.stop()
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
    print('sendProcessExperimentMessage')
    guid = None

    if not ADDRESS:
        raise ValueError("No EventHubs URL supplied.")                                    

    try:
        #loop = asyncio.get_event_loop()
        #client = EventHubClient(ADDRESS, debug=True, username=USER, password=KEY)
        client = EventHubClientAsync(ADDRESS, debug=True, username=USER, password=KEY)

        payload, guid = _getProcessExperimentPayload( MessageId,
                                                experimentName, 
                                                srcImageFolder,
                                                destinationFolder,
                                                imageBatchSize, 
                                                pos,
                                                partOfFileName)

        #tasks = asyncio.gather(sendMessageAsync(client, payload))
        #start_time = time.time()
        # loop.run_until_complete(tasks)
        # loop.run_until_complete(client.stop_async())
        await sendMessageAsync(client, payload, next(pool)) 
       

        #end_time = time.time()
        #run_time = end_time - start_time
        #print("Runtime: {} seconds".format(run_time))
        #loop.close()                                                

        #sender = client.add_sender(partition=next(pool)) 
        #sender = client.add_sender(partition=next(pool)) 
        #client.run()
        # sender.send(EventData(r))
        #logger.info("Runtime: {} seconds".format(run_time))
    except Exception as e:
        raise
    finally:
        #client.stop()
        pass
    return   guid                                  


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

async def sendDetectorMessages(MessageId,experimentName,destinationFolder):
    global ADDRESS
    global USER
    global KEY
    global pool
    print('sendDetectorMessages')
    guid = None

    if not ADDRESS:
        raise ValueError("No EventHubs URL supplied.")                                    

    lstGuids = []
    client = EventHubClientAsync(ADDRESS, debug=True, username=USER, password=KEY)
    for key, value in detectorsTypes.items():
        r, guid = _getDetectorTypeMessagePayload(MessageId, experimentName, destinationFolder, value )
        lstGuids.append(json.dumps({experimentName:guid}))
        try:
            await sendMessageAsync(client, r, "0") # we need only one instance of these running! 
        except Exception as e:
            raise
        finally:
            pass
    return   lstGuids      
