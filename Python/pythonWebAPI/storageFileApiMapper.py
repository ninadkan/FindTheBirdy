
import sys
sys.path.insert(0, '../') # needed as common is in the parent folder
import storageFileService

from flask import Flask, jsonify, abort, make_response
from flask import send_file
import json
import io

import numpy as np
import cv2
import os


def GetRawSourceImageImpl(storageObj, request):
    if not request.json or not '_sourceFileShareFolderName' in request.json \
        or not '_sourceDirectoryName' in request.json \
        or not '_imageFileName' in request.json:
        abort(400)

    result, description, image_binary = storageObj.GetRawSourceImageImpl(  request.json['_sourceFileShareFolderName'],
                                                                request.json['_sourceDirectoryName'],
                                                                request.json['_imageFileName'])

    if (result == True):
        binary_image = io.BytesIO(image_binary)
        binary_image.seek(0)
        return send_file(binary_image,mimetype='image/jpeg')
    else:
        return make_response(jsonify({'error': image_binary}), 500)    


def GetMaskedImage(storageObj, request):
    if not request.json or not '_sourceFileShareFolderName' in request.json \
        or not '_sourceDirectoryName' in request.json \
        or not '_imageFileName' in request.json \
        or not '_maskTags' in request.json:
        abort(400)

    result, description, image_binary = storageObj.GetMaskedImageImpl( request.json['_sourceFileShareFolderName'],
                                    request.json['_sourceDirectoryName'],
                                    request.json['_imageFileName'],
                                    request.json['_maskTags'])

    if (result == True):
        binary_image = io.BytesIO(image_binary)
        binary_image.seek(0)
        return send_file(binary_image,mimetype='image/jpeg')
    else:
        
        return make_response(jsonify({'error': image_binary}), 500)

def CopySourceDestination(storageObj, request):
    if not request.json or not '_sourceFileShareFolderName' in request.json \
        or not '_sourceDirectoryName' in request.json \
        or not '_destinationFileShareFolderName' in request.json \
        or not '_destinationDirectoryName' in request.json \
        or not '_ExperimentName' in request.json \
        or not '_fileExtensionFilter' in request.json:
        abort(400)

    # result, description = deleteAllFiles(request.json['_destinationFileShareFolderName'],
    #                                 request.json['_destinationDirectoryName'])

    result, description = storageObj.CopySourceDestinationImpl( request.json['_sourceFileShareFolderName'],
                                    request.json['_sourceDirectoryName'],
                                    request.json['_destinationFileShareFolderName'],
                                    request.json['_destinationDirectoryName'],
                                    request.json['_ExperimentName'],
                                    request.json['_fileExtensionFilter'])
    if (result == False):
        return make_response(jsonify({'error': description}), 500)
    else:
        return jsonify({'result': result, 'elapsedTime':description})

def GetAllExperimentsWithMaskAndImageFile(storageObj, request):
    if not request.json or not '_sourceFileShareFolderName' in request.json \
        or not '_sourceDirectoryName' in request.json :
        abort(400)

    result, obj = storageObj.GetAllExperimentsWithMaskAndImageFileImpl(request.json['_sourceFileShareFolderName'],
                                                     request.json['_sourceDirectoryName'])
    if (result == True):
        #print(json.dumps(obj))
        return json.dumps(obj)
    else:
        return make_response(jsonify({'error': obj}), 500)

def SaveMaskFileData(storageObj, request):
    if not request.json or not '_sourceFileShareFolderName' in request.json \
        or not '_sourceDirectoryName' in request.json \
        or not '_maskTags' in request.json:
        abort(400)

    result, description, = storageObj.SaveMaskFileDataImpl( request.json['_sourceFileShareFolderName'],
                                                        request.json['_sourceDirectoryName'],
                                                        request.json['_maskTags'])

    #print(description)
    if (result == False):
        return make_response(jsonify({'error': description}), 500)
    else:
        return jsonify({'elaspsedTime': description})

def GetAllExperimentsFilesNotCopied(storageObj, request):
    if not request.json or not '_destinationFileShareFolderName' in request.json \
        or not '_destinationDirectoryName' in request.json \
        or not '_experimentNames' in request.json:
        abort(400)

    result, description, rlist = storageObj.GetAllExperimentsFilesNotCopiedImpl( request.json['_destinationFileShareFolderName'],
                                                                        request.json['_destinationDirectoryName'],
                                                                        request.json['_experimentNames'])
    if (result == False):
        return make_response(jsonify({'error': description}), 500)
    else:
        return jsonify({'result': rlist,  'elapsedTime':description})


def GetAllSourceUniqueExperimentNames(storageObj, request):
    if not request.json or not '_sourceFileShareFolderName' in request.json \
        or not '_sourceDirectoryName' in request.json :
        abort(400)
    print("GetAllSourceUniqueExperimentNames")
    fileFilter = '.jpg'
    if '_fileExtensionFilter' in request.json:
        fileFilter = request.json['_fileExtensionFilter']

    result, description, rlist = storageObj.GetAllSourceUniqueExperimentNamesImpl(request.json['_sourceFileShareFolderName'],
                                                     request.json['_sourceDirectoryName'], fileFilter)
    if (result == False):
        return make_response(jsonify({'error': description}), 500)
    else:
        return jsonify({'result': rlist, 'elapsedTime':description})


def GetAllDestinationExperimentsWhereMaskFileNotPresent(storageObj, request):
    if not request.json or not '_destinationFileShareFolderName' in request.json \
        or not '_destinationDirectoryName' in request.json \
        or not '_experimentNames' in request.json:
        abort(400)

    result, description, rlist = storageObj.GetAllDestinationExperimentsWhereMaskFileNotPresentImpl( request.json['_destinationFileShareFolderName'],
                                                                        request.json['_destinationDirectoryName'],
                                                                        request.json['_experimentNames'])
    if (result == False):
        return make_response(jsonify({'error': description}), 500)
    else:
        return jsonify({'result': rlist,  'elapsedTime':description})


def GetAllDestinationUniqueExperimentNames(storageObj, request):
    if not request.json or not '_destinationFileShareFolderName' in request.json \
        or not '_destinationDirectoryName' in request.json :
        abort(400)

    result, description, rlist = storageObj.GetAllDestinationUniqueExperimentNamesImpl(request.json['_destinationFileShareFolderName'],
                                                                                  request.json['_destinationDirectoryName'] )
    
    if (result == False):
        return make_response(jsonify({'error': description}), 500)
    else:
        return jsonify({'result': rlist, 'elapsedTime':description})


def GetAllDestinationExperimentNamesWithOutputFiles(storageObj, request):
    if not request.json or not '_destinationFileShareFolderName' in request.json \
        or not '_destinationDirectoryName' in request.json \
        or not '_outputFolderName' in request.json :
        abort(400)

    fileExtension = '.jpg'
    if '_fileExtensionFilter' in request.json:
        fileExtension = request.json['_fileExtensionFilter']

    result, description, rlist = storageObj.GetAllDestinationExperimentNamesWithOutputFilesImpl(request.json['_destinationFileShareFolderName'],
                                                                                                        request.json['_destinationDirectoryName'],
                                                                                                        request.json['_outputFolderName'], 
                                                                                                        fileExtension )
    if (result == False):
        return make_response(jsonify({'error': description}), 500)
    else:
        return jsonify({'result': rlist, 'elapsedTime':description})



def DashBoardGetAllFilesInfo(storageObj, request):
    if not request.json or not '_sourceFileShareFolderName' in request.json \
    or not '_sourceDirectoryName' in request.json  \
    or not '_destinationFileShareFolderName' in request.json \
    or not '_destinationDirectoryName' in request.json \
    or not '_outputFolderName' in request.json:
        abort(400)

    fileFilter = '.jpg'
    if '_fileExtensionFilter' in request.json:
        fileFilter = request.json['_fileExtensionFilter']

    result, description, rlist = storageObj.DashBoardGetAllFilesInfoImpl(
                                                        request.json['_sourceFileShareFolderName'],
                                                        request.json['_sourceDirectoryName'],
                                                        request.json['_destinationFileShareFolderName'],
                                                        request.json['_destinationDirectoryName'], 
                                                        request.json['_outputFolderName'], 
                                                        _fileExtensionFilter=fileFilter)
    if (result == False):
        return make_response(jsonify({'error': description}), 500)
    else:
        return jsonify({'result': rlist, 'elapsedTime':description})


def DashBoardGetAllSourceFilesInfo(storageObj, request):
    if not request.json or not '_sourceFileShareFolderName' in request.json \
        or not '_sourceDirectoryName' in request.json :
        abort(400)

    fileFilter = '.jpg'
    if '_fileExtensionFilter' in request.json:
        fileFilter = request.json['_fileExtensionFilter']
    result, description, rlist = storageObj.DashBoardGetAllSourceFilesInfoImplWrapper(
                                                            request.json['_sourceFileShareFolderName'],
                                                            request.json['_sourceDirectoryName'], 
                                                            fileFilter)
    if (result == False):
        return make_response(jsonify({'error': description}), 500)
    else:
        return jsonify({'result': rlist, 'elapsedTime':description})

def DashBoardGetAllDestinationFilesInfo(storageObj, request):
    if not request.json or not '_destinationFileShareFolderName' in request.json \
    or not '_destinationDirectoryName' in request.json \
    or not '_outputFolderName' in request.json:
        abort(400)

    fileFilter = '.jpg'
    if '_fileExtensionFilter' in request.json:
        fileFilter = request.json['_fileExtensionFilter']

    result, description, rlist = storageObj.DashBoardGetAllDestinationFilesInfoImplWrapper(
                                                        request.json['_destinationFileShareFolderName'],
                                                        request.json['_destinationDirectoryName'], 
                                                        request.json['_outputFolderName'], 
                                                        _fileExtensionFilter=fileFilter)
    
    if (result == False):
        print(description)
        return make_response(jsonify({'error': description}), 500)
    else:
        return jsonify({'result': rlist, 'elapsedTime':description})
