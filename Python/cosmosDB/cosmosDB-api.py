#!flask/bin/python
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from flask_cors import CORS
from  cosmosDBWrapper import clsCosmosWrapper
import json

import sys
sys.path.insert(0, '../')
import common

clsObj = None

app = Flask(__name__)
CORS(app)


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


@app.route('/comsosDB/v1.0/collections', methods=['GET'])
def get_collections():
    global clsObj
    if (clsObj == None):
        clsObj = clsCosmosWrapper()
   
    result, link = clsObj.returnAllCollection()
    return jsonify({'result': result})

@app.route('/comsosDB/v1.0/documents', methods=['POST'])
def get_documents():
    if not request.json or not 'collectionLink' in request.json:
        abort(400)

    collectionLink = request.json['collectionLink']
    global clsObj
    if (clsObj == None):
        clsObj = clsCosmosWrapper()
   

    result = clsObj.returnAllDocuments(collectionLink)
    return jsonify({'result': result})

@app.route('/comsosDB/v1.0/document', methods=['GET'])
def get_document():
    
    from urllib.parse import unquote
    docId = request.args.get('docId')
    if not docId:
        abort(400)
    docId = unquote(docId)
    
    global clsObj
    if (clsObj == None):
        clsObj = clsCosmosWrapper()
   
   
    result = clsObj.returnDocument(docId)
    return jsonify(result)

# @app.route('/comsosDB/v1.0/insert_doc_collection', methods=['POST'])
# def insert_document_in_collection():
#     from urllib.parse import unquote
#     collectionId = request.args.get('collId')
#     if not collectionId:
#          abort(400)

#     if not 'id' in request.json or not 'detectedItems' in request.json:
#         abort(400)
#     global clsObj
#     result = clsObj.insert_document_in_collection(collectionId, request.json["id"], request.json["detectedItems"])
#     return jsonify(result)

# @app.route('/comsosDB/v1.0/get_doc_collection', methods=['GET'])
# def get_document_in_collection():
#     print("Processing Insert Document")

#     from urllib.parse import unquote
#     collectionId = request.args.get('collId')
#     if not collectionId:
#         print('collectionid is not correct!!!')
#         abort(400)
#     docId = request.args.get('docId')
#     if not docId:
#         print('docId parameter is not correct!!!')
#         abort(400)  

#     global clsObj
#     result = clsObj.queryDocsForExistence(collectionId, docId)
#     return jsonify(result)

@app.route('/comsosDB/v1.0/saveLabelledImageList', methods=['POST'])
def saveLabelledImageList():
    if not request.json or not common._DETECTED_IMAGES_TAG in request.json \
        or not common._EXPERIMENTNAME_TAG in request.json \
        or not common._IMAGE_DETECTION_PROVIDER_TAG in request.json :
        abort(400)

    global clsObj
    if (clsObj == None):
        clsObj = clsCosmosWrapper()
   

    clsObj.saveLabelledImageListImpl(   request.json[common._IMAGE_DETECTION_PROVIDER_TAG],
                                        request.json[common._EXPERIMENTNAME_TAG],
                                        request.json)
    return make_response(jsonify({'OK': 'OK'}), 200)

@app.route('/comsosDB/v1.0/returnLabelledImageList', methods=['POST'])
def returnLabelledImageList():
    if not request.json or not common._IMAGE_DETECTION_PROVIDER_TAG in request.json \
        or not common._EXPERIMENTNAME_TAG in request.json:
        abort(400)

    global clsObj
    if (clsObj == None):
        clsObj = clsCosmosWrapper()

    rv = clsObj.returnLabelledImageListImpl(request.json[common._IMAGE_DETECTION_PROVIDER_TAG],
                                            request.json[common._EXPERIMENTNAME_TAG])
    
    if (rv == None):
        return make_response(jsonify({'error': 'OK'}), 500)
    else:
        return make_response(json.dumps({'result': rv}), 200)


@app.route('/comsosDB/v1.0/returnAllExperimentResult', methods=['GET'])
def returnAllExperimentResult():
    global clsObj
    if (clsObj == None):
        clsObj = clsCosmosWrapper()
   
    rv = clsObj.returnAllExperimentResultImpl()
    
    if (rv == None):
        return make_response(jsonify({'error': 'OK'}), 500)
    else:
        return jsonify(rv)


if __name__ == '__main__':
    # print ("executing the main")
    clsObj = clsCosmosWrapper()
    # app.run(debug=True, host='0.0.0.0', port=5001)
    # as we go under docker, gunicorn and nginx will forward any request and 
    # will worry about port mappings , does mean that running this locally with 
    # python cosmosDB-api.py command might fail with port conflict and not available. 
    app.run(debug=True)
    # NOT TRUE; THIS CODE OF MAIN IS NOT EXECUTED ME THINKS AS THE __name__ is ! 'main'