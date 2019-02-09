from azure.eventhub import EventHubClient, Sender, EventData
import json
import os
import datetime
import common

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
    return r, str(messageId)
                               

def sendStartExperimentMessage(experimentNames):

    global ADDRESS
    global USER
    global KEY
    
    if not ADDRESS:
        raise ValueError("No EventHubs URL supplied.") 
    lstGuids = []
    try:
        client = EventHubClient(ADDRESS, debug=True, username=USER, password=KEY)
        sender = client.add_sender() # deliberately not specifying the partition keys
        client.run()
        for experimentName in experimentNames:
            #logger.info("Sending message: {}".format(i))
            r, guid = _getStartExperimentMessagePayload(experimentName)
            lstGuids.append(json.dumps({experimentName:guid}))
            sender.send(EventData(r))
            #logger.info("Runtime: {} seconds".format(run_time))
    except Exception as e:
        raise
    finally:
        client.stop()
    return   lstGuids

def sendProcessExperimentMessage(   MessageId,
                                    experimentName, 
                                    srcImageFolder,
                                    destinationFolder,
                                    imageBatchSize, 
                                    pos,
                                    partOfFileName):
    global ADDRESS
    global USER
    global KEY
    
    if not ADDRESS:
        raise ValueError("No EventHubs URL supplied.")                                    

    try:
        client = EventHubClient(ADDRESS, debug=True, username=USER, password=KEY)
        sender = client.add_sender() # deliberately not specifying the partition keys
        client.run()
        r, guid = _getProcessExperimentPayload( MessageId,
                                                experimentName, 
                                                srcImageFolder,
                                                destinationFolder,
                                                imageBatchSize, 
                                                pos,
                                                partOfFileName)
        sender.send(EventData(r))
        #logger.info("Runtime: {} seconds".format(run_time))
    except Exception as e:
        raise
    finally:
        client.stop()
    return   guid                                  
 