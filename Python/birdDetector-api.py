#!flask/bin/python
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from flask_cors import CORS
from flask import send_file


import io
import json
#import azureFileShareTest
#import mask_creation
import openCVPhotoExtractorTest as ctrl

app = Flask(__name__)
CORS(app)



@app.route('/birdDetector/v1.0/processExperiment', methods=['POST'])
def processExperiment():
    if not request.json or not 'experimentName' in request.json
        abort(400)

    experimentNames = request.json['_destinationFileShareFolderName']
    if (ctrlcheckExportKeysSetup() == True):
        if (delete_existing_files(experimentNames) == True) :
            runExperiments(experimentNames)
            return jsonify({'result': rlist, 'elapsedTime':description})
        else:
            return make_response(jsonify({'error': "Unable to delete folders"}), 500)
    else:
        return make_response(jsonify({'error': "Environment not set-up correctly"}), 500)

        





if __name__ == '__main__':
    # curl --header "Content-Type:application/json" --request POST --data {'_sourceFileShareFolderName': 'linuxraspshare', '_sourceDirectoryName': 'backup', '_destinationFileShareFolderName': 'experiment-data', '_destinationDirectoryName': 'object-detection', '_ExperimentName': '2018-04-15', '_fileExtensionFilter': '.jpg'} http://localhost:5000/azureStorage/v1.0/CopySourceDestination
    # Above line does not work eversince CORS has been added as you need a shakehand
    # Below statement works with http (NOT TESTED WITH HTTPS) working with CORS 
    # Pay special attention to space after ':' in the -H specification
    # only works in Command line (DOS) and not under Windows PowerShell environment!!!
    # only works if all the parameters are enclised with double quotes and not single quotes. Single quotes don't work
    # Working statement
    # curl -H "Content-Type: application/json" -H "Origin: http://localhost" -H "Access-Control-Request-Method: POST" -d "{\"_sourceFileShareFolderName\":\"experiment-data\",\"_sourceDirectoryName\":\"object-detection\"}" --verbose http://localhost:5000/azureStorage/v1.0/GetAllSourceUniqueExperimentNames
    # if you want to just check that the CORS bit is working, you can send the pre-post message as below
    # curl -H "Origin: http://localhost" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: X-Requested-With" -X OPTIONS --verbose http://localhost:5000/azureStorage/v1.0/GetAllSourceUniqueExperimentNames
    # example of request - response
    # 
    # *   Trying ::1...
    # * TCP_NODELAY set
    # * Connected to localhost (::1) port 5000 (#0)
    # > OPTIONS /azureStorage/v1.0/GetAllSourceUniqueExperimentNames HTTP/1.1
    # > Host: localhost:5000
    # > User-Agent: curl/7.62.0
    # > Accept: */*
    # > Origin: http://localhost
    # > Access-Control-Request-Method: POST
    # > Access-Control-Request-Headers: X-Requested-With
    # >
    # * HTTP 1.0, assume close after body
    # < HTTP/1.0 200 OK
    # < Content-Type: text/html; charset=utf-8
    # < Allow: OPTIONS, POST
    # < Access-Control-Allow-Origin: http://localhost
    # < Access-Control-Allow-Headers: X-Requested-With
    # < Access-Control-Allow-Methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
    # < Vary: Origin
    # < Content-Length: 0
    # < Server: Werkzeug/0.14.1 Python/3.6.8
    # < Date: Sat, 19 Jan 2019 14:19:50 GMT
    #app.run(debug=True, host='0.0.0.0:')
    app.run(debug=True)