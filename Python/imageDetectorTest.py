#to use this file, uncomment the required stub and invoke

# from mobileNetImageDetector import processImages
# Detector = "Mobile Net Detector"

# from yoloBirdImageDetector import processImages, verbosity
# Detector = "Yolo Detector"

# Need to set environment variable AZURE_VISION_API_KEY
# Py36 environment
#from azureImageDetector import processImages, verbosity
#Detector = "Azure Detector"

# Need to activate py27 environment
# set environment key 
# export GOOGLE_APPLICATION_CREDENTIALS=<path_to_service_account_file>
from googleImageDetector import processImages, verbosity
Detector = "Google Detector"

import time

start_time = time.time()
TotalBirdsFound  = processImages()
end_time = time.time() - start_time

print("")
print(Detector)                
print("Total bird images found  = {0}".format(TotalBirdsFound) + "  " + "Elapsed time = " + time.strftime("%H:%M:%S", time.gmtime(end_time)))


