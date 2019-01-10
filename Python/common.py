from pathlib import Path


_FileShare = True # if this is set, it is assumed that the mount/share is not used and https:// is to be used. 
_UseDocker = True

_SRCIMAGEFOLDER = None
_DESTINATIONFOLDER = None
_FileShareName = None


if (_FileShare) :
    _FileShareName = str('experiment-data')
    _SRCIMAGEFOLDER = str('object-detection')
else:
    #_SRCIMAGEFOLDER = str(Path('E:/object-detection'))
    #_SRCIMAGEFOLDER = str(Path('C:\\Users\\ninadk\\Downloads\\GardenPhotos\\backup\\Birds\\'))
    _SRCIMAGEFOLDER = str(Path('C:/Users/ninadk/Downloads/GardenPhotos/backup/object-detection'))
    
_DESTINATIONFOLDER = str(Path('output/'))
_FILENAMEEXTENSION = '.jpg'
_PARTOFFILENAME = ''
_BATCH_SIZE =25


_COLLECTIONAME = 'ImageDetectionResults'
_DATETIME_TAG = "DateTime"
_ELAPSED_TIME_TAG = "ElapsedTime"
_IMAGE_TAG = "bird"


_DETECTED_IMAGES_TAG = 'detectedItems'
_EXPERIMENTNAME_TAG = 'ExperimentName'

_IMAGE_DETECTION_PROVIDER_TAG = 'ImageDetectionProvider'
_ID_FOR_USER_DETECTION = 'userDetection',

_IMAGE_NAME_TAG = 'ImageName'
_CONFIDENCE_SCORE_TAG = 'ConfidenceScore'

_ARGS_OFFSET="--offset"
_ARGS_SRC_IMAGE_FOLDER="--srcImageFolder"
_ARGS_DESTINATION_FOLDER="--destinationFolder"
_ARGS_FILE_NAME_EXTENSTION="--filenameExtension"
_ARGS_EXPERIMENT_NAME="--experimentName"
_ARGS_BATCH_SIZE="--imageBatchSize"
_ARGS_PART_OF_FILE_NAME="--partOfFileName"
_ARGS_NUMBER_OF_IMAGES_TO_PROCESS="--numberOfImagesToProcess"

_ARGS_NUM_IMAGES_TO_CREATE_BKGRND="--numImagesToCreateMeanBackground"
_ARGS_GRAY_THRESHOLD="--grayImageThreshold"
_ARGS_BOUNDING_RECT_AREA_THRESHOLD="--boundingRectAreaThreshold"
_ARGS_CONTOUR_COUNT_THRESHOLD="--contourCountThreshold"
_ARGS_MASK_DIFF_THRESHOLD="--maskDiffThreshold"
_ARGS_WRITE_OUTPUT="--writeOutput"
_ARGS_LOG_RESULT="--logResult"


    

