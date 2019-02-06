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

app = Flask(__name__)
CORS(app)

from azure.eventhub import EventHubClient, Sender, EventData
import json

ADDRESS = os.environ.get('EVENT_HUB_ADDRESS')
# SAS policy and key are not required if they are encoded in the URL
USER = os.environ.get('EVENT_HUB_SENDER_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SENDER_SAS_KEY')

def getStartExperimentMessagePayload(experimentName):
    import uuid
    messageId = uuid.uuid4()
    currentDate = datetime.datetime.now()
    r = json.dumps({ common._MESSAGE_TYPE_TAG: common._MESSAGE_TYPE_START_EXPERIMENT, 'MessageId': str(messageId), 'ExperimentName': experimentName, 'CreationDateTime' : currentDate.strftime("%c")} )
    return r, str(messageId)


@app.route('/birdDetector/v1.0/processExperiments', methods=['POST'])
def processExperiments():
    if not request.json or not 'experimentNames' in request.json \
        or not isinstance(request.json['experimentNames'], list):
        abort(400)

    global ADDRESS
    global USER
    global KEY
    
    if not ADDRESS:
        raise ValueError("No EventHubs URL supplied.")

    start_time = datetime.datetime.now()
    

    lstGuids = []
    experimentNames = request.json['experimentNames']
    # get a guid for the experimentName, to uniquely identify this request
    # and send it back to the client. 
    try:
        client = EventHubClient(ADDRESS, debug=True, username=USER, password=KEY)
        sender = client.add_sender() # deliberately not specifying the partition keys
        client.run()
        for experimentName in experimentNames:
            #logger.info("Sending message: {}".format(i))
            r, guid = getStartExperimentMessagePayload(experimentName)
            lstGuids.append(json.dumps({experimentName:guid}))
            sender.send(EventData(r))
            #logger.info("Runtime: {} seconds".format(run_time))
    except Exception as e:
        raise
    finally:
        client.stop()

    time_elapsed = datetime.datetime.now() - start_time 
    elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)


    return jsonify({'result': lstGuids, 'elapsedTime':elapsedTime})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5002)
    # specifying host='127.0.0.1' is as good as not specifying. its default
    # specifying host='127.0.0.1:5002' is error, specify port= separately. 
    #app.run(debug=True)
    # Test suite
    # curl -H "Content-Type: application/json" -H "Origin: http://localhost" -H "Access-Control-Request-Method: POST" -d "{\"experimentNames\" : [\"2018-04-15\", \"2018-04-16\", \"2018-04-17\", \"2018-04-18\", \"2018-04-19\", \"2018-04-20\", \"2018-04-21\", \"2018-04-22\", \"2018-04-23\", \"2018-04-24\"]}" --verbose http://localhost:5002/birdDetector/v1.0/processExperiments