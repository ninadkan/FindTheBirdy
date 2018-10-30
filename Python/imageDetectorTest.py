#from mobileNetImageDetector import processImages
#Detector = "Mobile Net Detector"

# from yoloBirdImageDetector import processImages, verbosity
# Detector = "Yolo Detector"

# from azureImageDetector import processImages, verbosity
# Detector = "Azure Detector"

from googleImageDetector import processImages, verbosity
Detector = "Google Detector"

import time

start_time = time.time()
TotalBirdsFound  = processImages()
end_time = time.time() - start_time

print("")
print(Detector)                
print("Total bird images found  = {0}".format(TotalBirdsFound) + "  " + "Elapsed time = " + time.strftime("%H:%M:%S", time.gmtime(end_time)))


