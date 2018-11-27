
import os
import sys
from azure.storage.file import FileService
from azureCommon import preCheck, maskFileName
import json
import datetime
  
def CopySourceDestinationImpl(  _sourceFileShareFolderName, _sourceDirectoryName, 
                            _destinationFileShareFolderName, _destinationDirectoryName, 
                            _ExperimentName, _fileExtensionFilter='.jpg'):
    '''
    This method copies raw data from the source directory to the experiment folder
    _sourceDirectoryName, _destinationDirectoryName: format should be directoryName/secondDirectoryName, no trailing 
    slashes.  
    '''
    
    start_time = datetime.datetime.now()
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
        
        time_elapsed = datetime.datetime.now() - start_time 
        elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
        return True, elapsedTime

def GetAllExperimentsWithMaskAndImageFileImpl(_destinationFileShareFolderName, _destinationDirectoryName, _fileExtensionFilter='.jpg'):
    rv, description, file_service, _accountName, _accountKey = preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
    if (rv == False):
        return rv, description
    else:
        returnList = []
        experimentList = list(file_service.list_directories_and_files(_destinationFileShareFolderName, directory_name=_destinationDirectoryName))

        if (not(experimentList is None and len(experimentList)<1)):
            for i, experimentName in enumerate(experimentList):
                filenameList = list(file_service.list_directories_and_files(_destinationFileShareFolderName, _destinationDirectoryName+ "/" + experimentName.name))
                if (not (filenameList is None and len(filenameList)<1)):
                    for j, filenameList in enumerate(filenameList):
                        maskContent = ''
                        # check if maskFile exists and load its content
                        if (file_service.exists(_destinationFileShareFolderName, _destinationDirectoryName+ "/" + experimentName.name, maskFileName) != False):
                            fileMask = file_service.get_file_to_text(_destinationFileShareFolderName, _destinationDirectoryName+ "/" + experimentName.name, maskFileName)
                            if (fileMask is not None and fileMask.content is not None and len(fileMask.content) >0 ):
                                maskContent = json.loads(fileMask.content)
                        # load name of first file with extsnsion = _fileExtensionFilter
                        if (filenameList.name.endswith(_fileExtensionFilter)):
                            myVar = {"experimentName":experimentName.name, "filename":filenameList.name, "maskContent": maskContent}
                            returnList.append(myVar)
                            # we've got our file, lets exit from this inner loop
                            break

    return True, returnList

def SaveMaskFileDataImpl(_sourceFileShareFolderName, _sourceDirectoryName, _maskTags):
    start_time = datetime.datetime.now()
    rv = False
    rv, description, file_service, _accountName, _accountKey  = preCheck(_sourceFileShareFolderName, _sourceDirectoryName)
    if (rv == False):
        return rv, description
    else: 
        if (_maskTags is None or len(_maskTags) == 0 ):
            return rv, "Invalid mask values!!!"
        else:
            masks = []
            bDataValid = False
            try:
                masks = json.loads(_maskTags)
                bDataValid = True
            except ValueError:
                pass
            
            if (bDataValid == True):
                if (masks is None or len(masks) == 0 ):
                    return rv, "Incorrect format of ask values!!!"
                else:
                    file_service.create_file_from_text(_sourceFileShareFolderName, _sourceDirectoryName, maskFileName, _maskTags)
                    time_elapsed = datetime.datetime.now() - start_time 
                    elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
                    return True, elapsedTime
            else:
                return rv, "masks passed cannot be converted to json objects"

def GetAllExperimentsFilesNotCopiedImpl(_destinationFileShareFolderName, _destinationDirectoryName, _experimentNames):
    '''
    This function expects parameter _experimentNames to contain a list of experimentNames. 
    It then checks if the destination folder has been created or not!.  if NOT, it then adds it to the list. 
    This function is used to figure out if the original source files have been copied or not. 
    If the destination experiment folder exists, it is assumed that the source files have been copied. 
    //TODO:: better implementation would be to check for filename in source and under experiment folder are same and check if those are 
    same. then return true, else return false. 
    '''

    start_time = datetime.datetime.now()
    rv = False
    rv, description, file_service, _accountName, _accountKey  = preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
    if (rv == False):
        return rv, description, None
    
    returnList = []

    for experimentName in (_experimentNames):
        if (file_service.exists(_destinationFileShareFolderName, _destinationDirectoryName+ "/" + experimentName) == False):
            returnList.append(experimentName)

    time_elapsed = datetime.datetime.now() - start_time 
    elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
    return True, elapsedTime, returnList    

def GetAllSourceUniqueExperimentNamesImpl(_sourceFileShareFolderName, _sourceDirectoryName, _fileExtensionFilter='.jpg'):
    '''
    This function is to be used @ the source folder, where the images are all clubbed together. and we want to extract out 
    the various experiment names that have been created. 
    In our context the _sourceFileShareFolderName = 'linuxraspshare' and '_sourceDirectoryName' = 'Share'
    '''
    start_time = datetime.datetime.now()
    rv = False
    rv, description, file_service, _accountName, _accountKey  = preCheck(_sourceFileShareFolderName, _sourceDirectoryName)
    if (rv == False):
        return rv, description, None
    returnList = []
    experimentList = list(file_service.list_directories_and_files(_sourceFileShareFolderName, _sourceDirectoryName))

    if (not(experimentList is None and len(experimentList)<1)):
        for i, experimentName in enumerate(experimentList):
            if (experimentName.name.endswith(_fileExtensionFilter)):
                n = experimentName.name.find('_')
                if (n > 0):
                    expName = experimentName.name[0:n]
                    if expName not in returnList:
                        returnList.append(expName)

    time_elapsed = datetime.datetime.now() - start_time 
    elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
    return True, elapsedTime,returnList

def GetAllDestinationExperimentsWhereMaskFileNotPresentImpl(_destinationFileShareFolderName, _destinationDirectoryName, _experimentNames):
    '''
    _experimentNames contains list of all the experiment names. 
    This function looks for existence of mask file under the destination folders and if it does not exists, marks that experiment 
    as not yet processed and returns that as part of the list. If the mask file exists under the destination folder, it is assumed 
    that the masking exercise has been done for that experiment
    '''
    start_time = datetime.datetime.now()
    rv = False
    rv, description, file_service, _accountName, _accountKey  = preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
    if (rv == False):
        return rv, description, None
    
    returnList = []

    for experimentName in (_experimentNames):
        # check if maskFile exists and load its content
        if (file_service.exists(_destinationFileShareFolderName, _destinationDirectoryName+ "/" + experimentName, maskFileName) == False):
            returnList.append(experimentName)

    time_elapsed = datetime.datetime.now() - start_time 
    elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
    return True, elapsedTime, returnList

def GetAllDestinationUniqueExperimentNamesImpl(_destinationFileShareFolderName, _destinationDirectoryName):
    '''
    This function returns the number of folders that currently exists under the destination folders. 
    _destinationFileShareFolderName = 'experiment'
    _destinationDirectoryName = 'object-detection'
    '''
    start_time = datetime.datetime.now()
    rv = False
    rv, description, file_service, _accountName, _accountKey  = preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
    if (rv == False):
        return rv, description, None
    returnList = []
    experimentList = list(file_service.list_directories_and_files(_destinationFileShareFolderName, _destinationDirectoryName))

    if (not(experimentList is None and len(experimentList)<1)):
        for i, experimentName in enumerate(experimentList):
            returnList.append(experimentName.name)

    time_elapsed = datetime.datetime.now() - start_time 
    elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
    return True, elapsedTime,returnList

def GetAllDestinationExperimentNamesWithOutputFilesImpl(    _destinationFileShareFolderName, 
                                                            _destinationDirectoryName,
                                                            _outputFolderName = 'output',
                                                            _fileExtensionFilter='.jpg'):
    '''
    This function returns the number of folders/experiment that currently exists under the destination folders. 
    plus it returns all the image files contained inside the outpur folder
    _destinationFileShareFolderName = 'experiment'
    _destinationDirectoryName = 'object-detection'
    '''
    start_time = datetime.datetime.now()
    rv = False
    rv, description, file_service, _accountName, _accountKey  = preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
    if (rv == False):
        return rv, description, None
    returnList = []
    experimentList = list(file_service.list_directories_and_files(_destinationFileShareFolderName, _destinationDirectoryName))

    if (not(experimentList is None and len(experimentList)<1)):
        for i, experimentName in enumerate(experimentList):
            outputFiles = []
            combinedFolderName = _destinationDirectoryName+"/"+experimentName.name+"/"+_outputFolderName
            #print(combinedFolderName)
            if (file_service.exists(_destinationFileShareFolderName, combinedFolderName)):
                fileList = list(file_service.list_directories_and_files(_destinationFileShareFolderName, combinedFolderName))
                if (not(fileList is None and len(fileList)<1)):
                    for j, fileName in enumerate(fileList):
                        if (fileName.name.endswith(_fileExtensionFilter)):
                            outputFiles.append(fileName.name)
            returnList.append({'experimentName':experimentName.name, 'outputFiles':outputFiles})

    time_elapsed = datetime.datetime.now() - start_time 
    elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
    return True, elapsedTime,returnList

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