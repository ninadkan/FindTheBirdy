
import os
import sys
from azure.storage.file import FileService


PhotoFilter = ['2018-04-15_',
              '2018-04-16_',
              '2018-04-21_',
              '2018-04-22_']

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

#_accountKey = os.environ.get('AZURE_STRG_ACN')
#_accountName = 'nkdsvm'
#_accountKey = 'd19WRpMDg3zbG8FGFdHH0fXnVq52+IVBMMWTIivE/4/DBOoi++1nzqc9swHTenVGrwK24OmP0EUPiDmaZrFhEA=='
_rootFileShareFolder = 'linuxraspshare' 

# New folder structure for the experiment. 
_experimentFolderName = 'experiment-findthebird'
_sourceFolder = 'data'
_processedImages = 'outputopencv'
filenameExtension = _FILENAMEEXTENSION = '.jpg'

file_service = FileService(account_name=_accountName, 
account_key=_accountKey)

# check for existence of share and create it if it does not exist
if (file_service.exists(_experimentFolderName) == False):
    file_service.create_share(_experimentFolderName)

# check the existence of directory and create it if it does not exist
if (file_service.exists(_experimentFolderName, directory_name=_sourceFolder) == False):
    file_service.create_directory(_experimentFolderName, _sourceFolder)

if (file_service.exists(_experimentFolderName, directory_name=_sourceFolder+"/"+_processedImages) == False):
    file_service.create_directory(_experimentFolderName, _sourceFolder+"/"+_processedImages)


rootDirectories = []
generator = file_service.list_directories_and_files(_rootFileShareFolder)
for file_or_dir in generator:
    print(file_or_dir.name)
    rootDirectories.append(file_or_dir.name)

folderName = 'backup' # folder where our images are contained
for shareName in rootDirectories:
    if (shareName == folderName):
        fileList = file_service.list_directories_and_files(_rootFileShareFolder, directory_name=shareName)
        for i, imageFileName in enumerate(fileList):
            for filtername in PhotoFilter:
                if ( filtername in imageFileName.name) and imageFileName.name.endswith(filenameExtension):
                    source = "https://{0}.file.core.windows.net/{1}/{2}/{3}".format(_accountName, _rootFileShareFolder,
                                                                        folderName, imageFileName.name )
                    print(source)
                    file_service.copy_file(_experimentFolderName, _sourceFolder, imageFileName.name, source )
                    break