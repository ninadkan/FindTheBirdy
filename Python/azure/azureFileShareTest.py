
import os
import sys
from azure.storage.file import FileService
from azureCommon import preCheck, maskFileName
import json


def exitIfNull(_key, environVariable):
    if (_key is None ) or (len(_key) == 0):
        return False, "Environment Variable {0} name not specified. Exiting".format(environVariable)
    
def CopySourceDestination(  _sourceFileShareFolderName, _sourceDirectoryName, 
                            _destinationFileShareFolderName, _destinationDirectoryName, 
                            _ExperimentName, _fileExtensionFilter='.jpg'):
    '''
    This method copies raw data from the source directory to the experiment folder
    _sourceDirectoryName, _destinationDirectoryName: format should be directoryName/secondDirectoryName, no trailing 
    slashes.  
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

def getAllExperimentsAndFirstFilesImpl(_sourceFileShareFolderName, _sourceDirectoryName, _fileExtensionFilter='.jpg'):
    rv, description, file_service, _accountName, _accountKey = preCheck(_sourceFileShareFolderName, _sourceDirectoryName)
    if (rv == False):
        return rv, description
    else:
        returnList = []
        experimentList = list(file_service.list_directories_and_files(_sourceFileShareFolderName, directory_name=_sourceDirectoryName))

        if (not(experimentList is None and len(experimentList)<1)):
            for i, experimentName in enumerate(experimentList):
                filenameList = list(file_service.list_directories_and_files(_sourceFileShareFolderName, _sourceDirectoryName+ "/" + experimentName.name))
                if (not (filenameList is None and len(filenameList)<1)):
                    for j, filenameList in enumerate(filenameList):
                        maskContent = ''
                        # check if maskFile exists and load its content
                        if (file_service.exists(_sourceFileShareFolderName, _sourceDirectoryName+ "/" + experimentName.name, maskFileName) != False):
                            fileMask = file_service.get_file_to_text(_sourceFileShareFolderName, _sourceDirectoryName+ "/" + experimentName.name, maskFileName)
                            if (fileMask is not None and fileMask.content is not None and len(fileMask.content) >0 ):
                                maskContent = json.loads(fileMask.content)
                        # load name of first file with extsnsion = _fileExtensionFilter
                        if (filenameList.name.endswith(_fileExtensionFilter)):
                            myVar = {"experimentName":experimentName.name, "filename":filenameList.name, "maskContent": maskContent}
                            returnList.append(myVar)
                            # we've got our file, lets exit from this inner loop
                            break

    return True, returnList









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