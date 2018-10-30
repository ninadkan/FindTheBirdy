
import os
import sys
from azure.storage.file import FileService

def exitIfNull(_key, environVariable):
    if (_key is None ) or (len(_key) == 0):
        print("Environment variable {0} name not specified. Exiting".format(environVariable))
        sys.exit(0)

AZURE_ACN_NAME = 'AZURE_ACN_NAME'
_accountName = os.environ.get(AZURE_ACN_NAME)
exitIfNull(_accountName, AZURE_ACN_NAME)

AZURE_ACN_STRG_KEY = 'AZURE_ACN_STRG_KEY'
_accountKey = os.environ.get(AZURE_ACN_STRG_KEY)
exitIfNull(_accountKey, AZURE_ACN_STRG_KEY)

# New folder structure for the experiment. 
_experimentFolderName = 'experiment-findthebird'
_sourceFolder = 'data'
_processedImages = 'outputopencv'
_filenameExtension = _FILENAMEEXTENSION = '.jpg'


def populateAzureFilelist(   partOfFileName = '', shareName = _experimentFolderName, 
                        directoryName = _sourceFolder, extensionName= _filenameExtension):
    fileList = []
    file_service = FileService(account_name=_accountName, 
    account_key=_accountKey)
    files = file_service.list_directories_and_files(shareName, directory_name=directoryName)
    for file in files:
        if file.endswith(extensionName):
            if (len(partOfFileName) >0):
                if (partOfFileName in file):
                    fileList.append(file)
            else:
                fileList.append(file)
    return fileList


