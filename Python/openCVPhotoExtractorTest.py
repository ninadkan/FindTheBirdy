#OpenCVPhotoExtractorTest
import time
from OpenCVPhotoExtractor import processImages, _DESTINATIONFOLDER, verbosity

BoundingRectList = [2500, 2000, 1500, 1000]

def delete_existing_files():
    import os
    for the_file in os.listdir(_DESTINATIONFOLDER):
        file_path = os.path.join(_DESTINATIONFOLDER, the_file)
        try:
            # this'll be different for UNIX/Linux systems. 
            cpCommand = "del  " + file_path 
            os.system(cpCommand)
        except Exception as e:
            print(e)
    return 


for item in BoundingRectList:
        delete_existing_files()
        l, t, tt, fp, fn = processImages(boundingRectAreaThreshold=item, numberOfIterations=-1)
        print ("")
        print("Bounding Rectangle value = {0}".format(item))                
        print("Elapsed time = " + time.strftime("%H:%M:%S", time.gmtime(t))+ "Total images processed = {0}".format(l))
        print ("True detection = {0:0.2f}, false +ve = {1:0.2f} , false negative = {2:0.2f}".format(tt, fp, fn))


