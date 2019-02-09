import json
import argparse
import requests
import common


def getLastOffset(partitionNumber):
    brv = False
    OFFSET = None
    #curl -H "Content-Type: application/json" -H "Origin: http://localhost" -H "Access-Control-Request-Method: POST" -d "{\"EventLog\":\"evLog\",\"ConsumerGroup\":\"cgGrp\",\"PartitionId\":\"2\"}" --verbose http://localhost:5000/comsosDBOperations/v1.0/operationsGetLastOffset
    payload = {"EventLog": USER, "ConsumerGroup": CONSUMER_GROUP, "PartitionId": partitionNumber, common._MESSAGE_TYPE_TAG:common._MESSAGE_TYPE_START_EXPERIMENT}
    brv, resp =  baseRequest(payload, 'operationsGetLastOffset')
    
    if resp.status_code != 200:
        print('Error : {0}'.format(resp.status_code))
    else:
        returnValue = resp.json()
        if (returnValue is not None and returnValue['result'] is not None):
            OFFSET = Offset(returnValue['result']) # returns -1 if no previous one are found. 
            print(returnValue['result'])
            brv = True
        else:
            print("json result does not contain result or offset")
    return brv, OFFSET
    
def updateNewOffset(partitionNumber, newOffset):
    #curl -H "Content-Type: application/json" -H "Origin: http://localhost" -H "Access-Control-Request-Method: POST" -d "{\"EventLog\":\"evLog\",\"ConsumerGroup\":\"cgGrp\",\"PartitionId\":\"2\",\"LastOffset\":\"101\"}" --verbose http://localhost:5000/comsosDBOperations/v1.0/operationsInsertLastOffsetDocument
    payload = { "EventLog": USER, "ConsumerGroup": CONSUMER_GROUP, "PartitionId": partitionNumber, \
                "LastOffset": newOffset, common._MESSAGE_TYPE_TAG:common._MESSAGE_TYPE_START_EXPERIMENT }
    return baseRequest(payload, 'operationsInsertLastOffsetDocument' )

def updateMessageProcessingStatus(messageID, experimentName,offset, currentCount, maxItems, elapsed_time,  statusMessage):
    payload = { "EventLog": USER, "ConsumerGroup": CONSUMER_GROUP, "PartitionId": partitionNumber, \
                "LastOffset": newOffset, common._MESSAGE_TYPE_TAG:common._MESSAGE_TYPE_START_EXPERIMENT }
    return baseRequest(payload, 'operationsInsertLastOffsetDocument')

def getMessageProcseeingStatus(messageID, experimentName):
    

def baseRequest(payload, urlfunctionName):
    url = 'http://localhost:5001/comsosDBOperations/v1.0/'
    brv = False
    returnValue = None
    resp = requests.post(url+ urlfunctionName,
                            data=json.dumps(payload),
                            headers={'Content-Type':'application/json'})
    if resp.status_code != 200:
        print('Error : {0}'.format(resp.status_code))
    else:
        returnValue = resp.json()
        brv = True
    return brv, returnValue


