"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
from flask import Flask, jsonify, abort, make_response
from flask import url_for
from flask import request, Response
from flask_cors import CORS
import json
import validateJWT
import appSecrets
import storageBlobService
import storageFileApiMapper
import securityImpl
import cosmosDBApiMapper

#import azureStorage.azureFileShareTest as azureFileShareTest
#import azureStorage.mask_creation as mask_creation

app = Flask(__name__)

CORS(app)

securityObj = securityImpl.securityImpl()

# Make the WSGI interface available at the top level so wfastcgi can get it.
# wsgi_app = app.wsgi_app

@app.errorhandler(401)
def custom_401(error):
    return Response('Unauthorized', 401, {'Content-Type': 'text/html', 'WWW-Authenticate':'Basic realm="Login Required"'})

@app.errorhandler(400)
def custom_400(error):
    return Response('Unauthorized', 400, {'Content-Type': 'text/html', 'WWW-Authenticate':'Basic realm="Consent Required"'})

@app.errorhandler(404)
def not_found(error):
     return make_response(jsonify({'error': 'Not found'}), 404)

# @app.route('/')
# def hello():
#     """Renders a sample page."""
#     return "Hello World!"

@app.route('/test/api/callback', methods=['GET'])
def test_callback():
    return jsonify({'OK': 'EverythingOK'})

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return coreValidationAndProcessing(request, get_tasksImpl)

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    return coreValidationAndProcessing(request, get_taskImpl, task_id)

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    return coreValidationAndProcessing(request, create_taskImpl)

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    return coreValidationAndProcessing(request, update_taskImpl, task_id)

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    return coreValidationAndProcessing(request, delete_taskImpl, task_id)

# =========================== Implementation   ============================== #
def coreValidationAndProcessing(request, funcInvoke, task_id=None):
    global securityObj
    bRV, re = securityObj.validateRequest(request)
    if (bRV):
        #storagefileObject = securityObj.get_fileStorageObject()
        tasks, storageBlobWrapper = readContentIntoTasks()
        if (task_id):
            return funcInvoke(task_id, tasks, storageBlobWrapper,request)
        else:
            return funcInvoke(tasks, storageBlobWrapper,request)
    else:
        return constructResponseObject(re)

def constructResponseObject(responsePassed):
    """
    constructs an Error response object, even if the 
    """
    if (responsePassed):
        temp_resp = Response()
        temp_resp.status_code = responsePassed.status_code or 404
        if((temp_resp.status_code >= 200) and (temp_resp.status_code < 300)):
            temp_resp.status_code = 404
            temp_resp.reason = 'Bad Request'
            details = 'UnexpectedError'
            temp_resp.headers = {'Content-Type': 'text/html', 'Warning': details}
        else:
            temp_resp.reason = responsePassed.reason or 'Bad Request'
            details = responsePassed.content or 'UnexpectedError'
            temp_resp.headers = {'Content-Type': 'text/html', 'WWW-Authenticate': details}
    else:
        temp_resp = Response()
        temp_resp.reason = 'Bad Request'
        temp_resp.status_code = 404
        details = 'UnexpectedError'
        temp_resp.headers = {'Content-Type': 'text/html', 'WWW-Authenticate': details}
    return temp_resp


def readContentIntoTasks():
    global securityObj
    storageBlobWrapper = securityObj.get_StorageObject()
    content = storageBlobWrapper.get_blob_content()
    tasks = None
    if (content and len(content)>0):
        tasks = json.loads(content)
    return tasks, storageBlobWrapper

def get_tasksImpl(tasks, storageBlobWrapper, request):
    return jsonify({'tasks': tasks})

def get_taskImpl(task_id, tasks, storageBlobWrapper, request):
    if (tasks == None or len(tasks) == 0):
        abort(404)
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})

def create_taskImpl(tasks, storageBlobWrapper, request):
    if not request.json or not 'title' in request.json:
        abort(400)

    if (tasks == None or len(tasks) == 0):
        tasks = list()
        task = {
            'id': 1,
            'title': request.json['title'],
            'description': request.json.get('description', ""),
            'done': False
        }
    else:
        task = {
            'id': tasks[-1]['id'] + 1,
            'title': request.json['title'],
            'description': request.json.get('description', ""),
            'done': False
        }
    tasks.append(task)
    storageBlobWrapper.update_blob_content(json.dumps(tasks))
    return jsonify({'task': task}), 201

def update_taskImpl(task_id, tasks, storageBlobWrapper, request):
    if (tasks == None or len(tasks) == 0):
        abort(404)

    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' not in request.json :
        abort(400)
    if 'description' not in request.json:
        abort(400)
    if 'done' not in request.json:
        abort(400)

    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    # save it back to storage
    for idx, item in enumerate(tasks):
        if (item['id'] == task_id):
            item['title'] = task[0]['title']
            item['description'] = task[0]['description']
            item['done'] = task[0]['done']
    storageBlobWrapper.update_blob_content(json.dumps(tasks))       
    return jsonify({'task': task[0]})

def delete_taskImpl(task_id, tasks, storageBlobWrapper, request):
    if (tasks == None or len(tasks) == 0):
        abort(404)

    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)

    tasks.remove(task[0])
    storageBlobWrapper.update_blob_content(json.dumps(tasks))     
    return jsonify({'result': True})

# =========================== Core security wrapper ========================= #

constObjectValue = 'clsobject'
constImageOperationsValue = 'clsimageoperations'
constStatusOperations = 'clsstatusoperations'
constStorageFileObject = 'storagefileobject' 

def ValidateSecurityAndProcessRequestCommon(request, funcInvoke, objectTypeRequired = 'storagefileobject'):
    global securityObj
    bRV, re = securityObj.validateRequest(request)
    if (bRV):
        invokerObject = None
        callObject = str(objectTypeRequired).lower()
        if ( callObject == constObjectValue) :
            invokerObject = securityObj.get_clsObject()
        else:
            if (callObject == constImageOperationsValue):
                invokerObject = securityObj.get_clsImageOperations()
            else:
                if (callObject == constStatusOperations):
                    invokerObject = securityObj.get_clsStatusOperations()
                else: 
                    if (callObject == constStorageFileObject):
                        invokerObject = securityObj.get_fileStorageObject()
        if (invokerObject):
            return funcInvoke(invokerObject, request)
        else :
            return constructResponseObject(None)

    else:
        return constructResponseObject(re)

def ValidateSecurityAndProcessRequest(request, funcInvoke):
    return ValidateSecurityAndProcessRequestCommon(request, funcInvoke)


# =========================== Core security wrapper ========================= #
# =========================== File Storage APIs ============================= #


@app.route('/azureStorage/v1.0/GetRawSourceImage', methods=['POST'])
def GetRawSourceImage():
    return ValidateSecurityAndProcessRequest(request, storageFileApiMapper.GetRawSourceImageImpl)

@app.route('/azureStorage/v1.0/GetMaskedImage', methods=['POST'])
def GetMaskedImage():
    return ValidateSecurityAndProcessRequest(request, storageFileApiMapper.GetMaskedImage)

@app.route('/azureStorage/v1.0/CopySourceDestination', methods=['POST'])
def CopySourceDestination():
    return ValidateSecurityAndProcessRequest(request, storageFileApiMapper.CopySourceDestination)

@app.route('/azureStorage/v1.0/GetAllExperimentsWithMaskAndImageFile', methods=['POST'])
def GetAllExperimentsWithMaskAndImageFile():
    return ValidateSecurityAndProcessRequest(request, storageFileApiMapper.GetAllExperimentsWithMaskAndImageFile)

@app.route('/azureStorage/v1.0/SaveMaskFileData', methods=['POST'])
def SaveMaskFileData():
    return ValidateSecurityAndProcessRequest(request, storageFileApiMapper.SaveMaskFileData)

@app.route('/azureStorage/v1.0/GetAllExperimentsFilesNotCopied', methods=['POST'])
def GetAllExperimentsFilesNotCopied():
    return ValidateSecurityAndProcessRequest(request, storageFileApiMapper.GetAllExperimentsFilesNotCopied)

@app.route('/azureStorage/v1.0/GetAllSourceUniqueExperimentNames', methods=['POST'])
def GetAllSourceUniqueExperimentNames():
    return ValidateSecurityAndProcessRequest(request, storageFileApiMapper.GetAllSourceUniqueExperimentNames)

@app.route('/azureStorage/v1.0/GetAllDestinationExperimentsWhereMaskFileNotPresent', methods=['POST'])
def GetAllDestinationExperimentsWhereMaskFileNotPresent():
    return ValidateSecurityAndProcessRequest(request, storageFileApiMapper.GetAllDestinationExperimentsWhereMaskFileNotPresent)

@app.route('/azureStorage/v1.0/GetAllDestinationUniqueExperimentNames', methods=['POST'])
def GetAllDestinationUniqueExperimentNames():
    return ValidateSecurityAndProcessRequest(request, storageFileApiMapper.GetAllDestinationUniqueExperimentNames)

@app.route('/azureStorage/v1.0/GetAllDestinationExperimentNamesWithOutputFiles', methods=['POST'])
def GetAllDestinationExperimentNamesWithOutputFiles():
    return ValidateSecurityAndProcessRequest(request, storageFileApiMapper.GetAllDestinationExperimentNamesWithOutputFiles)

@app.route('/azureStorage/v1.0/DashBoardGetAllFilesInfo', methods=['POST'])
def DashBoardGetAllFilesInfo():
    return ValidateSecurityAndProcessRequest(request, storageFileApiMapper.DashBoardGetAllFilesInfo)

@app.route('/azureStorage/v1.0/DashBoardGetAllSourceFilesInfo', methods=['POST'])
def DashBoardGetAllSourceFilesInfo():
    return ValidateSecurityAndProcessRequest(request, storageFileApiMapper.DashBoardGetAllSourceFilesInfo)

@app.route('/azureStorage/v1.0/DashBoardGetAllDestinationFilesInfo', methods=['POST'])
def DashBoardGetAllDestinationFilesInfo():
    return ValidateSecurityAndProcessRequest(request, storageFileApiMapper.DashBoardGetAllDestinationFilesInfo)

# =========================== File Storage APIs ============================= #
# =========================== Cosmos APIs =================================== # 
@app.route('/cosmosDB/v1.0/collections', methods=['GET'])
def get_collections():
    return ValidateSecurityAndProcessRequestCommon(request, cosmosDBApiMapper.get_collections, constObjectValue)
 
@app.route('/cosmosDB/v1.0/documents', methods=['POST'])
def get_documents():
    return ValidateSecurityAndProcessRequestCommon(request, cosmosDBApiMapper.get_documents, constObjectValue)

@app.route('/cosmosDB/v1.0/getDocument', methods=['POST'])
def get_document():
    return ValidateSecurityAndProcessRequestCommon(request, cosmosDBApiMapper.get_document, constObjectValue)

@app.route('/cosmosDB/v1.0/saveLabelledImageList', methods=['POST'])
def saveLabelledImageList():
    return ValidateSecurityAndProcessRequestCommon(request, cosmosDBApiMapper.saveLabelledImageList, constObjectValue)

@app.route('/cosmosDB/v1.0/returnLabelledImageList', methods=['POST'])
def returnLabelledImageList():
    return ValidateSecurityAndProcessRequestCommon(request, cosmosDBApiMapper.returnLabelledImageList, constObjectValue)

@app.route('/cosmosDB/v1.0/returnAllExperimentResult', methods=['GET'])
def returnAllExperimentResult():
    return ValidateSecurityAndProcessRequestCommon(request, cosmosDBApiMapper.returnAllExperimentResult, constObjectValue)

###############################################################################
# Image Processsing Operations 
###############################################################################

@app.route('/cosmosDB/v1.0/operationsInsertLastOffsetDocument', methods=['POST'])
def operationsInsertLastOffsetDocument():
    return ValidateSecurityAndProcessRequestCommon(request, cosmosDBApiMapper.operationsInsertLastOffsetDocument, constImageOperationsValue)

@app.route('/cosmosDB/v1.0/operationsGetLastOffset', methods=['POST'])
def operationsGetLastOffset():
    return ValidateSecurityAndProcessRequestCommon(request, cosmosDBApiMapper.operationsGetLastOffset, constImageOperationsValue)

@app.route('/cosmosDB/v1.0/removeLastOffsetRecord', methods=['POST'])
def removeLastOffsetRecord():
    return ValidateSecurityAndProcessRequestCommon(request, cosmosDBApiMapper.removeLastOffsetRecord, constImageOperationsValue)

@app.route('/cosmosDB/v1.0/removeExistingDocumentDict', methods=['POST'])
def removeExistingDocumentDict():
    return ValidateSecurityAndProcessRequestCommon(request, cosmosDBApiMapper.removeExistingDocumentDict, constImageOperationsValue)

###############################################################################
# Operations Status 
###############################################################################

@app.route('/cosmosDB/v1.0/returnAllMessageIdGroupedList', methods=['GET'])
def returnAllMessageIdGroupedList():
    return ValidateSecurityAndProcessRequestCommon(request, cosmosDBApiMapper.returnAllMessageIdGroupedList, constStatusOperations)

@app.route('/cosmosDB/v1.0/removeAllDocumentsForSpecificMessageId', methods=['POST'])
def removeAllDocumentsForSpecificMessageId():
    return ValidateSecurityAndProcessRequestCommon(request, cosmosDBApiMapper.removeAllDocumentsForSpecificMessageId, constStatusOperations)

@app.route('/cosmosDB/v1.0/removeExistingDocumentDictStatus', methods=['POST'])
def removeExistingDocumentDictStatus():
    return ValidateSecurityAndProcessRequestCommon(request, cosmosDBApiMapper.removeExistingDocumentDictStatus, constStatusOperations)

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(debug=True,host=HOST, port=PORT)