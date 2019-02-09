from pathlib import Path


_FileShare = True # if this is set, it is assumed that the mount/share is not used and https:// is to be used. 
_UseDocker = False # if this is true, then we switch to invoking docker to process images. 
_UseEventHub = True # indicating that we are using EventHub to communicate our messages. 

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
_BATCH_SIZE =350


_COLLECTIONAME = 'ResultsImageDetection'
_OPERATIONSCOLLECTIONNAME = 'Operations'
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

# EventLog Common bits

_NUMBER_OF_EVENT_HUB_PARTITIONS = int(4) 

_MESSAGE_TYPE_TAG='MessageType'

_MESSAGE_TYPE_START_EXPERIMENT= 'START_EXPERIMENT'
_MESSAGE_TYPE_START_EXPERIMENT_EXPERIMENT_NAME = 'ExperimentName'
_MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID = 'MessageId'
_MESSAGE_TYPE_START_EXPERIMENT_CREATION_DATE_TIME = 'CreationDateTime'

_MESSAGE_TYPE_PROCESS_EXPERIMENT = 'PROCESS_EXPERIMENT'
_MESSAGE_TYPE_PROCESS_EXPERIMENT_EXPERIMENT_NAME = _MESSAGE_TYPE_START_EXPERIMENT_EXPERIMENT_NAME
_MESSAGE_TYPE_PROCESS_EXPERIMENT_MESSAGE_ID = _MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID
_MESSAGE_TYPE_PROCESS_EXPERIMENT_CREATION_DATE_TIME = _MESSAGE_TYPE_START_EXPERIMENT_CREATION_DATE_TIME
_MESSAGE_TYPE_PROCESS_EXPERIMENT_SRC_IMG_FOLDER = 'srcImageFolder'
_MESSAGE_TYPE_PROCESS_EXPERIMENT_DEST_FOLDER = 'destinationFolder'
_MESSAGE_TYPE_PROCESS_EXPERIMENT_BATCH_SIZE ='imageBatchSize' 
_MESSAGE_TYPE_PROCESS_EXPERIMENT_OFFSET_POSITION ='offsetPosition'
_MESSAGE_TYPE_PROCESS_EXPERIMENT_PART_OF_FILE_NAME='partOfFileName'

# cosmodDB opertions Messages
_OPERATIONS_EVENTLOG_TAG = "EventLog"
_OPERATIONS_CONSUMER_GROUP_TAG = "ConsumerGroup"
_OPERATIONS_PARTITION_ID = "PartitionId"
_OPERATIONS_LAST_OFFSET = "LastOffset"

_OPERATIONS_STATUS_MESSAGE_ID = _MESSAGE_TYPE_START_EXPERIMENT_MESSAGE_ID
_OPERATIONS_STATUS_EXPERIMENT_NAME = _MESSAGE_TYPE_START_EXPERIMENT_EXPERIMENT_NAME
_OPERATIONS_STATUS_OFFSET = 'Offset_Value'
_OPERATIONS_STATUS_CURRENT_COUNT = 'CurrentCount'
_OPERATIONS_STATUS_MAX_ITEMS = 'MaxItems'
_OPERATIONS_STATUS_ELAPSED_TIME = 'Time'
_OPERATIONS_STATUS_STATUS_MESSAGE = 'Status'





    

