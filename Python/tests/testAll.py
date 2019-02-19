
import sys
sys.path.insert(0, '../') # needed as common is in the parent folder
import common
import requests
import json


from common import _SRCIMAGEFOLDER, _FileShareName
import azureFS.azureFileShareTest as fs

rv, elapsedTime, ExperimentNames = fs.TestGetAllExperimentNames(_FileShareName, _SRCIMAGEFOLDER)
if (rv):
    lstExpnames = []
    for item in ExperimentNames:
        lstExpnames.append(item.name)
    print(lstExpnames)
    url = "http://localhost:5002/birdDetector/v1.0/processExperiments"
    #data = {'sender': 'Alice', 'receiver': 'Bob', 'message': 'We did it!'}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = {'experimentNames': lstExpnames }
    r = requests.post(url, data=json.dumps(data), headers=headers)