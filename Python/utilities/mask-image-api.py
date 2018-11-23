#!flask/bin/python
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from flask_cors import CORS
from  azureFileShareTest import CopySourceDestination, deleteAllFiles

app = Flask(__name__)
CORS(app)


@app.route('/maskAPi/v1.0/GetImage', methods=['Get'])
def GetImageMask():
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

    print('CopySourceDestination ... Validation Passed')


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



if __name__ == '__main__':
    #curl --header "Content-Type: application/json" --request POST --data {'_sourceFileShareFolderName': 'linuxraspshare', '_sourceDirectoryName': 'backup', '_destinationFileShareFolderName': 'experiment-data', '_destinationDirectoryName': 'object-detection', '_ExperimentName': '2018-04-15', '_fileExtensionFilter': '.jpg'} http://localhost:5000/azureStorage/v1.0/CopySourceDestination
    app.run(debug=True)








