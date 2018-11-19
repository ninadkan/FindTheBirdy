
import os
import sys
from azure.storage.file import FileService


# PhotoFilter = ['2018-04-15_',
#               '2018-04-16_',
#               '2018-04-21_',
#               '2018-04-22_']



def exitIfNull(_key, environVariable):
    if (_key is None ) or (len(_key) == 0):
        return False, "Environment variable {0} name not specified. Exiting".format(environVariable)
    
def CopySourceDestination(  _sourceFileShareFolderName, _sourceDirectoryName, 
                            _destinationFileShareFolderName, _destinationDirectoryName, 
                            _ExperimentName, _fileExtensionFilter='.jpg'):
    '''
    _sourceDirectoryName, _destinationDirectoryName: format should be directoryName/secondDirectoryName/
    '''
    rv, description, file_service, _accountName, _accountKey  = preCheck(_sourceFileShareFolderName, _sourceDirectoryName)
    if (rv == False):
        return rv, description
    else: 
        # check for existence of destination share and create it if it does not exist
        if (file_service.exists(_destinationFileShareFolderName) == False):
            file_service.create_share(_destinationFileShareFolderName)

        # check the existence of destination directory and create it if it does not exist
        if (file_service.exists(_destinationFileShareFolderName, directory_name=_destinationDirectoryName) == False):
            file_service.create_directory(_destinationFileShareFolderName, _destinationDirectoryName)

        # check the existence of destination experiment folder and create it if it does not exist 

        combinedDestinationFolderName = _destinationDirectoryName+"/"+_ExperimentName

        if (file_service.exists(_destinationFileShareFolderName, directory_name=combinedDestinationFolderName) == False):
            file_service.create_directory(_destinationFileShareFolderName, combinedDestinationFolderName)


        fileList = list(file_service.list_directories_and_files(_sourceFileShareFolderName, directory_name=_sourceDirectoryName))

        if (fileList is None and len(fileList)<1):
            return False, "No files found @ source"
        else:
            for i, imageFileName in enumerate(fileList):
                #print(imageFileName.name)
                if (( _ExperimentName in imageFileName.name) and imageFileName.name.endswith(_fileExtensionFilter)):
                    source = "https://{0}.file.core.windows.net/{1}/{2}/{3}".format(_accountName, _sourceFileShareFolderName,
                                                                        _sourceDirectoryName, imageFileName.name )
                    #print(source)
                    copy = file_service.copy_file(_destinationFileShareFolderName, combinedDestinationFolderName, imageFileName.name, source )


                    # Poll for copy completion
                    while copy.status != 'success':
                        count = count + 1
                        if count > 5:
                            return False, 'Timed out waiting for async copy to complete., Filename = {0} '.format(imageFileName) 
                        time.sleep(5)
                        copy = self.service.get_file_properties(_destinationFileShareFolderName, combinedDestinationFolderName, imageFileName.name).properties.copy



        return True, "OK"

def deleteAllFiles(_sourceFileShareFolderName, _sourceDirectoryName, _fileExtensionFilter='.jpg' ):
    rv, description, file_service, _accountName, _accountKey = preCheck(_sourceFileShareFolderName, _sourceDirectoryName)
    if (rv == False):
        return rv, description
    else:
        fileList = list(file_service.list_directories_and_files(_sourceFileShareFolderName, directory_name=_sourceDirectoryName))

        if (fileList is None and len(fileList)<1):
            return False, "No files found @ source"
        else:
            for i, imageFileName in enumerate(fileList):
                if (imageFileName.name.endswith(_fileExtensionFilter)):
                    source = "https://{0}.file.core.windows.net/{1}/{2}/{3}".format(_accountName, _sourceFileShareFolderName,
                                                                        _sourceDirectoryName, imageFileName.name )
                    copy = file_service.delete_file(_sourceFileShareFolderName, _sourceDirectoryName, imageFileName.name)
    return True, "OK"


def preCheck(_sourceFileShareFolderName, _sourceDirectoryName):
    AZURE_ACN_NAME = 'AZURE_ACN_NAME'
    _accountName = os.environ.get(AZURE_ACN_NAME)
    if (_accountName is None ) or (len(_accountName) == 0):
        return false , 'AZURE_ACN_NAME Environment Variable not set', None, None, None

    AZURE_ACN_STRG_KEY = 'AZURE_ACN_STRG_KEY'
    _accountKey = os.environ.get(AZURE_ACN_STRG_KEY)
    if (_accountKey is None ) or (len(_accountKey) == 0):
        return false , 'AZURE_ACN_STRG_KEY Environment Variable not set', None  , None, None    

    file_service = FileService(account_name=_accountName, 
    account_key=_accountKey)

    # Can we create file_share service
    if (file_service is None):
        return False, "Unable to create File share, check Account Name, Key and connectivity", None, None, None

    # check for existence of Source share folder
    if (file_service.exists(_sourceFileShareFolderName) == False):
        return False, "source share does not exist", None, None, None

    # check for existence of source share directory 
    if (file_service.exists(_sourceFileShareFolderName, directory_name=_sourceDirectoryName) == False):
        return False, "source directory does not exist", None, None, None

    return True, "OK", file_service, _accountName, _accountKey






if __name__ == "__main__":
    CopySourceDestination('linuxraspshare', 'Share', 'experiment-data', 'object-detection', '2018-11-09_')

# rootDirectories = []
# generator = file_service.list_directories_and_files(_sourceFileShareFolderName)
# for file_or_dir in generator:
#     print(file_or_dir.name)
#     rootDirectories.append(file_or_dir.name)
# folderName = 'backup' # folder where our images are contained
# for shareName in rootDirectories:
#     if (shareName == folderName):
#         fileList = file_service.list_directories_and_files(_sourceFileShareFolderName, directory_name=shareName)
#         for i, imageFileName in enumerate(fileList):
#             for filtername in PhotoFilter:
#                 if ( filtername in imageFileName.name) and imageFileName.name.endswith(_fileExtensionFilter):
#                     source = "https://{0}.file.core.windows.net/{1}/{2}/{3}".format(_accountName, _sourceFileShareFolderName,
#                                                                         folderName, imageFileName.name )
#                     print(source)
#                     file_service.copy_file(_destinationFileShareFolderName, _sourceDirectoryName, imageFileName.name, source )
#                     break