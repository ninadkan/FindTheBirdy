from flask import Flask, jsonify, abort, make_response
import json
import common

import logging
from loggingBase import getGlobalHandler, getGlobalLogObject, clsLoggingBase
g_logObj = getGlobalLogObject(__name__)


def get_collections(clsObj, request):
    global g_logObj
    g_logObj.debug("get_collections")

    result, link = clsObj.returnAllCollection()
    return jsonify({'result': result})

def get_documents(clsObj, request):
    global g_logObj
    g_logObj.debug("get_documents")
    if not request.json or not 'collectionLink' in request.json:
        abort(400)
    collectionLink = request.json['collectionLink']
    result = clsObj.returnAllDocuments(collectionLink)
    return jsonify({'result': result})

def get_document(clsObj, request):
    global g_logObj
    g_logObj.debug("get_document")

    from urllib.parse import unquote
    # docId = request.args.get('docId')
    # if not docId:
    #     print('document not in query')
    if not request.json or not 'docId' in request.json:
        print('document not in headers')
        abort(400)
    else: 
        docId = request.json['docId']
    #    abort(400)

    docId = unquote(docId)
   
    result = clsObj.returnDocument(docId)
    return jsonify(result)

def saveLabelledImageList(clsObj, request):
    global g_logObj
    g_logObj.debug("saveLabelledImageList")

    if not request.json or not common._DETECTED_IMAGES_TAG in request.json \
        or not common._EXPERIMENTNAME_TAG in request.json \
        or not common._IMAGE_DETECTION_PROVIDER_TAG in request.json :
        abort(400)

    clsObj.saveLabelledImageListImpl(   request.json[common._IMAGE_DETECTION_PROVIDER_TAG],
                                        request.json[common._EXPERIMENTNAME_TAG],
                                        request.json)
    return make_response(jsonify({'OK': 'OK'}), 200)

def returnLabelledImageList(clsObj, request):
    global g_logObj
    g_logObj.debug("returnLabelledImageList")

    if not request.json or not common._IMAGE_DETECTION_PROVIDER_TAG in request.json \
        or not common._EXPERIMENTNAME_TAG in request.json:
        abort(400)

    rv = clsObj.returnLabelledImageListImpl(request.json[common._IMAGE_DETECTION_PROVIDER_TAG],
                                            request.json[common._EXPERIMENTNAME_TAG])
    
    if (rv == None):
        return make_response(jsonify({'error': 'OK'}), 500)
    else:
        return make_response(json.dumps({'result': rv}), 200)

def returnAllExperimentResult(clsObj, request):

    global g_logObj
    g_logObj.debug("returnAllExperimentResult")

    rv = clsObj.returnAllExperimentResultImpl()
    
    if (rv == None):
        return make_response(jsonify({'error': 'OK'}), 500)
    else:
        return jsonify(rv)

###############################################################################
# Image Processsing Operations 
###############################################################################
def operationsInsertLastOffsetDocument(clsImageOperations, request):
    global g_logObj
    g_logObj.debug("operationsInsertLastOffsetDocument")

    if not request.json or not common._OPERATIONS_EVENTLOG_TAG in request.json \
        or not common._OPERATIONS_CONSUMER_GROUP_TAG in request.json \
        or not common._OPERATIONS_PARTITION_ID in request.json \
        or not common._OPERATIONS_LAST_OFFSET in request.json \
        or not common._MESSAGE_TYPE_TAG in request.json: 
        abort(400)

    rv = clsImageOperations.insert_offset_document_from_dict(request.json)
    
    if (rv == None):
        return make_response(jsonify({'error': 'OK'}), 500)
    else:
        return make_response(json.dumps({'result': rv}), 200)

def operationsGetLastOffset(clsImageOperations, request):

    global g_logObj
    g_logObj.debug("operationsGetLastOffset")

    if not request.json or not common._OPERATIONS_EVENTLOG_TAG in request.json \
        or not common._OPERATIONS_CONSUMER_GROUP_TAG in request.json \
        or not common._OPERATIONS_PARTITION_ID in request.json \
        or not common._MESSAGE_TYPE_TAG in request.json: 
        abort(400)

    rv = clsImageOperations.get_offsetValue( request.json[common._OPERATIONS_EVENTLOG_TAG],
                                        request.json[common._OPERATIONS_CONSUMER_GROUP_TAG],
                                        request.json[common._OPERATIONS_PARTITION_ID],
                                        request.json[common._MESSAGE_TYPE_TAG])
    if (rv == None):
        return make_response(jsonify({'error': 'OK'}), 500)
    else:
        return make_response(json.dumps({'result': rv}), 200)

def removeLastOffsetRecord(clsImageOperations, request):

    global g_logObj
    g_logObj.debug("removeLastOffsetRecord")

    if not request.json or not common._OPERATIONS_EVENTLOG_TAG in request.json \
        or not common._OPERATIONS_CONSUMER_GROUP_TAG in request.json \
        or not common._OPERATIONS_PARTITION_ID in request.json \
        or not common._MESSAGE_TYPE_TAG in request.json: 
        abort(400)

    clsImageOperations.removeOffsetExistingDocument(  request.json[common._OPERATIONS_EVENTLOG_TAG],
                                                request.json[common._OPERATIONS_CONSUMER_GROUP_TAG],
                                                request.json[common._OPERATIONS_PARTITION_ID],
                                                request.json[common._MESSAGE_TYPE_TAG])
    # this method does not return value; the only way to check if this has worked is to check that 
    # this method returned 200 and query for the same record and it should return -1
    return make_response(json.dumps({'result': "OK"}), 200)

def removeExistingDocumentDict(clsImageOperations, request):

    global g_logObj
    g_logObj.debug("removeExistingDocumentDict")
    
    if not request.json or not 'id' in request.json:
        abort(400)
    dictObject = {'id':request.json['id']}
    rv = clsImageOperations.removeOffsetExistingDocumentDict(dictObject, True)
    if (rv == None):
        return make_response(jsonify({'error': 'OK'}), 500)
    else:
        return make_response(json.dumps({'result': rv}), 200)

###############################################################################
# Operations Status 
###############################################################################
def returnAllMessageIdGroupedList(clsStatusOperations, request):
    global g_logObj
    g_logObj.debug("returnAllMessageIdGroupedList")

    rv = clsStatusOperations.returnAllMessageIdGroupedListImpl()
    
    if (rv == None):
        return make_response(jsonify({'error': 'OK'}), 500)
    else:
        return jsonify(rv)


def removeAllDocumentsForSpecificMessageId(clsStatusOperations, request):
    global g_logObj
    g_logObj.debug("removeAllDocumentsForSpecificMessageId")

    if not request.json or not common._MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID in request.json: 
        abort(400)

    rv = clsStatusOperations.removeAllDocumentsForSpecificMessageIdImpl(request.json[common._MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID])
    
    if (rv == None):
        return make_response(jsonify({'error': 'OK'}), 500)
    else:
        return jsonify(rv)


def removeExistingDocumentDictStatus(clsStatusOperations, request):

    global g_logObj
    g_logObj.debug("removeExistingDocumentDictStatus")

    if not request.json or not 'id' in request.json:
        abort(400)
    dictObject = {'id':request.json['id']}
    rv = clsStatusOperations.removeExistingDocumentDict(dictObject, True)
    if (rv == None):
        return make_response(jsonify({'error': 'OK'}), 500)
    else:
        return make_response(json.dumps({'result': rv}), 200)



# if __name__ == '__main__':
#     # print ("executing the main")
#     clsObj = clsCosmosWrapper()
#     # app.run(debug=True, host='0.0.0.0', port=5001)
#     # as we go under docker, gunicorn and nginx will forward any request and 
#     # will worry about port mappings , does mean that running this locally with 
#     # python cosmosDB-api.py command might fail with port conflict and not available. 
#     app.run(debug=True, host='127.0.0.1', port='5001')
#     # NOT TRUE; THIS CODE OF MAIN IS NOT EXECUTED ME THINKS AS THE __name__ is ! 'main'
#     # Test suite 
#     # First Testing CORS
#     # curl -H "Origin: http://localhost" -H "Access-Control-Request-Method: GET" -H "Access-Control-Request-Headers: X-Requested-With" -X OPTIONS --verbose http://localhost:5000/comsosDB/v1.0/returnAllExperimentResult
#     # Testing actual execution
#     # curl -H "Origin: http://localhost" -H "Access-Control-Request-Method: GET" --verbose http://localhost:5001/comsosDB/v1.0/returnAllExperimentResult  
#     # curl -H "Origin: http://localhost" -H "Access-Control-Request-Method: GET" --verbose http://localhost:5001/comsosDB/v1.0/returnAllMessageIdGroupedList
#     # curl -H "Origin: http://localhost" -H "Access-Control-Request-Method: GET" --verbose http://localhost:5001/comsosDB/v1.0/collections
#     # take the output from , extract "_self": "dbs/gsUdAA==/colls/gsUdAIR+xjM=/" from "id": "ResultsImageDetection" and use that to invoke the next test, which will return a lots of records. 
#     # curl -H "Content-Type: application/json" -H "Origin: http://localhost" -H "Access-Control-Request-Method: POST" -d "{\"collectionLink\":\"dbs/gsUdAA==/colls/gsUdAIR+xjM=/\"}" --verbose http://localhost:5001/comsosDB/v1.0/documents
#     # create a record
#     # curl -H "Content-Type: application/json" -H "Origin: http://localhost" -H "Access-Control-Request-Method: POST" -d "{\"EventLog\":\"evLog\",\"ConsumerGroup\":\"cgGrp\",\"PartitionId\":\"2\",\"LastOffset\":\"101\", \"MessageType\":\"START_EXPERIMENT\" }" --verbose http://localhost:5001/comsosDBOperations/v1.0/operationsInsertLastOffsetDocument
#     # retrieve previously created record
#     # curl -H "Content-Type: application/json" -H "Origin: http://localhost" -H "Access-Control-Request-Method: POST" -d "{\"EventLog\":\"evLog\",\"ConsumerGroup\":\"cgGrp\",\"PartitionId\":\"2\", \"MessageType\":\"START_EXPERIMENT\"}" --verbose http://localhost:5001/comsosDBOperations/v1.0/operationsGetLastOffset
#     # remove that previosly created record
#     # curl -H "Content-Type: application/json" -H "Origin: http://localhost" -H "Access-Control-Request-Method: POST" -d "{\"EventLog\":\"evLog\",\"ConsumerGroup\":\"cgGrp\",\"PartitionId\":\"2\", \"MessageType\":\"START_EXPERIMENT\"}" --verbose http://localhost:5001/comsosDBOperations/v1.0/removeLastOffsetRecord
