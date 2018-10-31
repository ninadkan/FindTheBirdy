#OpenCVPhotoExtractorTest
import time
from openCVPhotoExtractor import processImages, _DESTINATIONFOLDER, g_verbosity
import platform 

BoundingRectList = [1000] # [2500, 2000, 1500, 1000]

osString = platform.platform()
NIX_DEFINED = True
if ('Windows' in osString):
    NIX_DEFINED = False


def delete_existing_files():
    import os

    if NIX_DEFINED:
        files = os.path.join(_DESTINATIONFOLDER,'*')
        cpCommand = "rm -r " +  files
    else:
        files = os.path.join(_DESTINATIONFOLDER,'*.*')
        cpCommand = "del /q " + files

    try:
        print(cpCommand)
        os.system(cpCommand)
    except Exception as e:
        print(e)
    return 


for item in BoundingRectList:
        delete_existing_files()
        # premature end of JPEG was detected with 2018-04-22_0247. Remove that image 
        l, t, tt, fp, fn = processImages()
        print ("")
        print("Bounding Rectangle value = {0}".format(item))                
        print("Elapsed time = " + time.strftime("%H:%M:%S", time.gmtime(t))+ "Total images processed = {0}".format(l))
        print ("True detection = {0:0.2f}, false +ve = {1:0.2f} , false negative = {2:0.2f}".format(tt, fp, fn))


