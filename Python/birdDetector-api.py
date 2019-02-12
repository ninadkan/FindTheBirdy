#!flask/bin/python
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from flask_cors import CORS
from flask import send_file
from flask import g



import io
import json
# import azureFileShareTest
# import mask_creation
# import openCVPhotoExtractorTest as ctrl
import uuid
import common
import os
import datetime
import time
import asyncio
import eventMessageSender as msgSender
import loggingBase
import asyncioBase


app = Flask(__name__)
CORS(app)


@app.route('/birdDetector/v1.0/processExperiments', methods=['POST'])
def processExperiments():
    if not request.json or not 'experimentNames' in request.json \
        or not isinstance(request.json['experimentNames'], list):
        abort(400)
    start_time = datetime.datetime.now()
    experimentNames = request.json['experimentNames']
    # get a guid for the experimentName, to uniquely identify this request
    # and send it back to the client.
    
    lstGuids = asyncioBase.get_set_event_loop().run_until_complete(msgSender.sendStartExperimentMessage(experimentNames))

    time_elapsed = datetime.datetime.now() - start_time 
    elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
    return jsonify({'result': lstGuids, 'elapsedTime':elapsedTime})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5002)
    # specifying host='127.0.0.1' is as good as not specifying. its default
    # specifying host='127.0.0.1:5002' is error, specify port= separately. 
    #app.run(debug=True)
    # Test suite
    # curl -H "Content-Type: application/json" -H "Origin: http://localhost" -H "Access-Control-Request-Method: POST" -d "{\"experimentNames\" : [\"2018-04-15\"]}" --verbose http://localhost:5002/birdDetector/v1.0/processExperiments
    # curl -H "Content-Type: application/json" -H "Origin: http://localhost" -H "Access-Control-Request-Method: POST" -d "{\"experimentNames\" : [\"2018-04-15\", \"2018-04-16\", \"2018-04-17\", \"2018-04-18\", \"2018-04-19\", \"2018-04-20\", \"2018-04-21\", \"2018-04-22\", \"2018-04-23\", \"2018-04-24\"]}" --verbose http://localhost:5002/birdDetector/v1.0/processExperiments