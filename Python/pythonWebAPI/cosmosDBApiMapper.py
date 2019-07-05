#!flask/bin/python
from flask import Flask, jsonify, abort, make_response
from  cosmosDBWrapper import clsCosmosWrapper
from cosmosImageOperations import clsCosmosImageProcessingOperations
from cosmosStatusUpdate import clsStatusUpdate
import json

import sys
sys.path.insert(0, '../')
import common


clsObj = None           # our global instance
clsImageOperations = None    # our global instance
clsStatusOperations = None

# tasks = [
#     {
#         'id': 1,
#         'title': u'Buy groceries',
#         'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
#         'done': False
#     },
#     {
#         'id': 2,
#         'title': u'Learn Python',
#         'description': u'Need to find a good Python tutorial on the web', 
#         'done': False
#     }
# ]

# from flask import url_for
# def make_public_task(task):
#     new_task = {}
#     for field in task:
#         if field == 'id':
#             new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
#         else:
#             new_task[field] = task[field]
#     return new_task

# @app.route('/todo/api/v1.0/tasks', methods=['GET'])
# def get_tasks():
#     return jsonify({'tasks': [make_public_task(task) for task in tasks]})

# @app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
# def get_task(task_id):
#     task = [task for task in tasks if task['id'] == task_id]
#     if len(task) == 0:
#         abort(404)
#     return jsonify({'task': task[0]})

# @app.errorhandler(404)
# def not_found(error):
#     return make_response(jsonify({'error': 'Not found'}), 404)

# from flask import request

# @app.route('/todo/api/v1.0/tasks', methods=['POST'])
# def create_task():
#     if not request.json or not 'title' in request.json:
#         abort(400)
#     task = {
#         'id': tasks[-1]['id'] + 1,
#         'title': request.json['title'],
#         'description': request.json.get('description', ""),
#         'done': False
#     }
#     tasks.append(task)
#     return jsonify({'task': task}), 201

# @app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
# def update_task(task_id):
#     task = [task for task in tasks if task['id'] == task_id]
#     if len(task) == 0:
#         abort(404)
#     if not request.json:
#         abort(400)
#     if 'title' in request.json and type(request.json['title']) != unicode:
#         abort(400)
#     if 'description' in request.json and type(request.json['description']) is not unicode:
#         abort(400)
#     if 'done' in request.json and type(request.json['done']) is not bool:
#         abort(400)
#     task[0]['title'] = request.json.get('title', task[0]['title'])
#     task[0]['description'] = request.json.get('description', task[0]['description'])
#     task[0]['done'] = request.json.get('done', task[0]['done'])
#     return jsonify({'task': task[0]})

# @app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
# def delete_task(task_id):
#     task = [task for task in tasks if task['id'] == task_id]
#     if len(task) == 0:
#         abort(404)
#     tasks.remove(task[0])
#     return jsonify({'result': True})


def get_collections(clsObj, request):
    result, link = clsObj.returnAllCollection()
    return jsonify({'result': result})

def get_documents(clsObj, request):
    if not request.json or not 'collectionLink' in request.json:
        abort(400)
    collectionLink = request.json['collectionLink']
    result = clsObj.returnAllDocuments(collectionLink)
    return jsonify({'result': result})

def get_document(clsObj, request):
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
    if not request.json or not common._DETECTED_IMAGES_TAG in request.json \
        or not common._EXPERIMENTNAME_TAG in request.json \
        or not common._IMAGE_DETECTION_PROVIDER_TAG in request.json :
        abort(400)

    clsObj.saveLabelledImageListImpl(   request.json[common._IMAGE_DETECTION_PROVIDER_TAG],
                                        request.json[common._EXPERIMENTNAME_TAG],
                                        request.json)
    return make_response(jsonify({'OK': 'OK'}), 200)

def returnLabelledImageList(clsObj, request):
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
   
    rv = clsObj.returnAllExperimentResultImpl()
    
    if (rv == None):
        return make_response(jsonify({'error': 'OK'}), 500)
    else:
        return jsonify(rv)

###############################################################################
# Image Processsing Operations 
###############################################################################
def operationsInsertLastOffsetDocument(clsImageOperations, request):

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

###############################################################################
# Operations Status 
###############################################################################


def returnAllMessageIdGroupedList(clsStatusOperations, request):
    rv = clsStatusOperations.returnAllMessageIdGroupedListImpl()
    
    if (rv == None):
        return make_response(jsonify({'error': 'OK'}), 500)
    else:
        return jsonify(rv)


def removeAllDocumentsForSpecificMessageId(clsStatusOperations, request):
    if not request.json or not common._MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID in request.json: 
        abort(400)

    rv = clsStatusOperations.removeAllDocumentsForSpecificMessageIdImpl(request.json[common._MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID])
    
    if (rv == None):
        return make_response(jsonify({'error': 'OK'}), 500)
    else:
        return jsonify(rv)

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
