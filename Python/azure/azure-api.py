#!flask/bin/python
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from flask_cors import CORS
from flask import send_file
from  azureFileShareTest import CopySourceDestination, deleteAllFiles, getAllExperimentsAndFirstFilesImpl, SaveMaskFileDataImpl
from mask_creation import GetMaskedImageImpl, GetRawSourceImageImpl
import io
import json

app = Flask(__name__)
CORS(app)


@app.route('/azureStorage/v1.0/CopySourceDestination', methods=['POST'])
def CopySourceDestinationAPI():
    # print('CopySourceDestination')
    # print(request)
    # print(request.data)
    # print(request.form)
    # print(request.json)
    if not request.json or not '_sourceFileShareFolderName' in request.json \
        or not '_sourceDirectoryName' in request.json \
        or not '_destinationFileShareFolderName' in request.json \
        or not '_destinationDirectoryName' in request.json \
        or not '_ExperimentName' in request.json \
        or not '_fileExtensionFilter' in request.json:
        abort(400)

    # result, description = deleteAllFiles(request.json['_destinationFileShareFolderName'],
    #                                 request.json['_destinationDirectoryName'])

    result, description = CopySourceDestination( request.json['_sourceFileShareFolderName'],
                                    request.json['_sourceDirectoryName'],
                                    request.json['_destinationFileShareFolderName'],
                                    request.json['_destinationDirectoryName'],
                                    request.json['_ExperimentName'],
                                    request.json['_fileExtensionFilter'])
    if (result == False):
        print(description)
        return make_response(jsonify({'error': description}), 500)
    else:
        return jsonify({'result': result})

@app.route('/azureStorage/v1.0/GetRawSourceImage', methods=['POST'])
def GetRawSourceImage():
    if not request.json or not '_sourceFileShareFolderName' in request.json \
        or not '_sourceDirectoryName' in request.json \
        or not '_imageFileName' in request.json:
        abort(400)

    result, description, image_binary = GetRawSourceImageImpl(  request.json['_sourceFileShareFolderName'],
                                                                request.json['_sourceDirectoryName'],
                                                                request.json['_imageFileName'])

    if (result == True):
        binary_image = io.BytesIO(image_binary)
        binary_image.seek(0)
        return send_file(binary_image,mimetype='image/jpeg')
    else:
        return make_response(jsonify({'error': image_binary}), 500)    


@app.route('/azureStorage/v1.0/GetMaskedImage', methods=['POST'])
def GetMaskedImage():
    if not request.json or not '_sourceFileShareFolderName' in request.json \
        or not '_sourceDirectoryName' in request.json \
        or not '_imageFileName' in request.json \
        or not '_maskTags' in request.json:
        abort(400)

    result, description, image_binary = GetMaskedImageImpl( request.json['_sourceFileShareFolderName'],
                                    request.json['_sourceDirectoryName'],
                                    request.json['_imageFileName'],
                                    request.json['_maskTags'])

    if (result == True):
        binary_image = io.BytesIO(image_binary)
        binary_image.seek(0)
        return send_file(binary_image,mimetype='image/jpeg')
    else:
        
        return make_response(jsonify({'error': image_binary}), 500)

@app.route('/azureStorage/v1.0/GetAllExperimentsAndFirstFiles', methods=['POST'])
def GetAllExperimentsAndFirstFiles():
    if not request.json or not '_sourceFileShareFolderName' in request.json \
        or not '_sourceDirectoryName' in request.json :
        abort(400)

    result, obj = getAllExperimentsAndFirstFilesImpl(request.json['_sourceFileShareFolderName'],
                                                     request.json['_sourceDirectoryName'])
    if (result == True):
        return json.dumps(obj)
    else:
        return make_response(jsonify({'error': obj}), 500)



@app.route('/azureStorage/v1.0/SaveMaskFileData', methods=['POST'])
def SaveMaskFileData():
    if not request.json or not '_sourceFileShareFolderName' in request.json \
        or not '_sourceDirectoryName' in request.json \
        or not '_maskTags' in request.json:
        abort(400)

    result, description = SaveMaskFileDataImpl( request.json['_sourceFileShareFolderName'],
                                                request.json['_sourceDirectoryName'],
                                                request.json['_maskTags'])
    print(description)
    if (result == False):
        return make_response(jsonify({'error': description}), 500)
    else:
        return jsonify({'result': description})


if __name__ == '__main__':
    #curl --header "Content-Type: application/json" --request POST --data {'_sourceFileShareFolderName': 'linuxraspshare', '_sourceDirectoryName': 'backup', '_destinationFileShareFolderName': 'experiment-data', '_destinationDirectoryName': 'object-detection', '_ExperimentName': '2018-04-15', '_fileExtensionFilter': '.jpg'} http://localhost:5000/azureStorage/v1.0/CopySourceDestination
    app.run(debug=True)