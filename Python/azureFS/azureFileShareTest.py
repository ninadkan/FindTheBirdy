
import os
import sys

#import azure.storage.file as azureFs
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
                if (_fileExtensionFilter is not None ):
                    if (imageFileName.name.endswith(_fileExtensionFilter)):
                        rv = file_service.delete_file(_sourceFileShareFolderName, _sourceDirectoryName, imageFileName.name)
                else:
                    rv =file_service.delete_file(_sourceFileShareFolderName, _sourceDirectoryName, imageFileName.name)
    return True, "OK"

def DashBoardGetAllFilesInfoImpl(   _sourceFileShareFolderName, 
                                    _sourceDirectoryNameList,
                                    _destinationFileShareFolderName, 
                                    _destinationDirectoryName,
                                    _outputFolderName = 'output', 
                                    _fileExtensionFilter='.jpg'):
    '''
    Mother of all functions and scans through each and every file and returns lots of information. Could take up-to 10 minutes to run
    ''' 
    start_time = datetime.datetime.now()  
    print('phase1')
    result, description, returnSourceDict = DashBoardGetAllSourceFilesInfoImpl(_sourceFileShareFolderName, _sourceDirectoryNameList, _fileExtensionFilter) 
    if (result == True):
        print('phase2')
        result, description, returnDestinationDict = DashBoardGetAllDestinationFilesInfoImpl(
                                                    _destinationFileShareFolderName, 
                                                    _destinationDirectoryName,
                                                    _outputFolderName ,
                                                    _fileExtensionFilter,
                                                    _returnDict = returnSourceDict)
        if (result == True):
            print('phase3')
            # combine the two dictionaries
            combinedDict = dict()
            for key in returnSourceDict:    # assumed to contain superset of keys
                if key not in combinedDict: 
                    combinedDict[key] = [0,0,False, 0, 0, False, 0, 0]
                combinedDict[key][0] = returnSourceDict[key][0]
                combinedDict[key][1] = returnSourceDict[key][1]

                if key in returnDestinationDict:
                    combinedDict[key][2] = returnDestinationDict[key][2]
                    combinedDict[key][3] = returnDestinationDict[key][3]
                    combinedDict[key][4] = returnDestinationDict[key][4]
                    combinedDict[key][5] = returnDestinationDict[key][5]
                    combinedDict[key][6] = returnDestinationDict[key][6]
                    combinedDict[key][7] = returnDestinationDict[key][7]
            
            return returnFormattedValue(start_time, True, "OK", combinedDict)
        else:
            return returnFormattedValue(start_time, result, description, None)
    else:
        returnFormattedValue(start_time, result, description, None)

def DashBoardGetAllSourceFilesInfoImplWrapper(_sourceFileShareFolderName, _sourceDirectoryNameList, _fileExtensionFilter='.jpg'):
    start_time = datetime.datetime.now()
    result, description, returnDict = DashBoardGetAllSourceFilesInfoImpl(_sourceFileShareFolderName, _sourceDirectoryNameList, _fileExtensionFilter)
    return returnFormattedValue(start_time, result, description, returnDict)

def DashBoardGetAllSourceFilesInfoImpl(_sourceFileShareFolderName, _sourceDirectoryNameList, _fileExtensionFilter='.jpg'):
    '''
    This function is to be used @ the source folder, where the images are all clubbed together. and we want to extract out 
    the various experiment names that have been created. 
    In our context the _sourceFileShareFolderName = 'linuxraspshare' and '_sourceDirectoryName' = 'Share'
    This could also be _sourceFileShareFolderName = 'linuxraspshare' and '_sourceDirectoryName' = 'backup' as this function 
    now caters for
    '''
    start_time = datetime.datetime.now()
    rv = False
    # check the existence of first source folder
    rv, description, file_service, _accountName, _accountKey  = preCheck(_sourceFileShareFolderName, _sourceDirectoryNameList[0])
    if (rv == False):
        return rv, description, None
    returnDict = dict()

    for _sourceDirectoryName in _sourceDirectoryNameList:
        experimentList = list(file_service.list_directories_and_files(_sourceFileShareFolderName, _sourceDirectoryName))

        if (not(experimentList is None and len(experimentList)<1)):
            for i, imageFileName in enumerate(experimentList):
                if (imageFileName.name.endswith(_fileExtensionFilter)):
                    fileProperties = file_service.get_file_properties(_sourceFileShareFolderName, _sourceDirectoryName, imageFileName.name)
                    fileLength = fileProperties.properties.content_length
                    n = imageFileName.name.find('_')
                    if (n > 0):
                        expName = imageFileName.name[0:n]
                        if expName not in returnDict:
                            returnDict[expName] = [1,fileLength,False, 0, 0, False, 0, 0]
                        else:
                            returnDict[expName][0] += 1
                            returnDict[expName][1] += fileLength
    return True, "OK", returnDict

def DashBoardGetAllDestinationFilesInfoImplWrapper( _destinationFileShareFolderName, 
                                                    _destinationDirectoryName,
                                                    _outputFolderName = 'output',
                                                    _fileExtensionFilter='.jpg',
                                                    _returnDict = None,
                                                    _file_service = None):
    start_time = datetime.datetime.now()
    result, description, returnDict = DashBoardGetAllDestinationFilesInfoImpl( _destinationFileShareFolderName, 
                                                                                _destinationDirectoryName,
                                                                                _outputFolderName ,
                                                                                _fileExtensionFilter,
                                                                                _returnDict ,
                                                                                _file_service )

    return returnFormattedValue(start_time, result, description, returnDict)

def DashBoardGetAllDestinationFilesInfoImpl(_destinationFileShareFolderName, 
                                            _destinationDirectoryName,
                                            _outputFolderName = 'output',
                                            _fileExtensionFilter='.jpg',
                                            _returnDict = None):
    start_time = datetime.datetime.now()
    rv = False
    file_service = None
    description = ''
    rv, description, file_service, _accountName, _accountKey  = preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
    if (rv == False):
        return rv, description, None
    
    returnDict = dict()
    if _returnDict is not None:
        returnDict = _returnDict
    else:     
        experimentList = list(file_service.list_directories_and_files(_destinationFileShareFolderName, _destinationDirectoryName))

        # 1st pass, get all the experiment names, which are provided by the folder names
        if (not(experimentList is None and len(experimentList)<1)):
            for i, experimentName in enumerate(experimentList):
                if experimentName.name not in returnDict:
                        # Mask file exists
                        # number of Files in the experiment root folder
                        # size of the files in the experiment root folder
                        # output folder exists
                        # number of files in the output folder
                        # size of files in the output folder.
                        returnDict[experimentName.name] = [0, 0, False, 0, 0, False, 0, 0]
    # 2nd pass, find all the properties of the images
    for key in returnDict:
        combinedFolderName = _destinationDirectoryName+"/"+ key
        if (file_service.exists(_destinationFileShareFolderName,combinedFolderName, maskFileName)):
            if _returnDict is None:
                 returnDict[key][0] = 0
                 returnDict[key][1] = 0
            
            returnDict[key][2] = True
            numberOfFiles , sizeOfFiles =  getNumberOfFilesAndFileSize(file_service,_destinationFileShareFolderName, combinedFolderName , _fileExtensionFilter )
            returnDict[key][3] = numberOfFiles
            returnDict[key][4] = sizeOfFiles
            combinedFolderName = _destinationDirectoryName+"/"+ key + "/" + _outputFolderName
            if (file_service.exists(_destinationFileShareFolderName,combinedFolderName)):
                returnDict[key][5] = True
                numberOfFiles , sizeOfFiles =  getNumberOfFilesAndFileSize(file_service, _destinationFileShareFolderName, combinedFolderName, _fileExtensionFilter )
                returnDict[key][6] = numberOfFiles
                returnDict[key][7] = sizeOfFiles
    
    return True, "OK", returnDict

def returnFormattedValue(start_time, result, description, returnDict):
    if (result == True):
        retValue = []
        for key, value in returnDict.items():
            item = {'ExperimentName': key, 'Properties': value}
            retValue.append(item)

        time_elapsed = datetime.datetime.now() - start_time 
        elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
    
        return True, elapsedTime,retValue
    else:
        return False, description, None

def getNumberOfFilesAndFileSize(file_service, shareFolder, directoryName, _fileExtensionFilter):
    numberOfFiles = 0
    sizeOfFiles = 0

    experimentList = list(file_service.list_directories_and_files(shareFolder, directoryName))

    if (not(experimentList is None and len(experimentList)<1)):
        for i, imageFileName in enumerate(experimentList):
            if (imageFileName.name.endswith(_fileExtensionFilter)):
                numberOfFiles += 1
                fileProperties = file_service.get_file_properties(shareFolder, directoryName, imageFileName.name)
                fileLength = fileProperties.properties.content_length
                sizeOfFiles += fileLength

    return numberOfFiles, sizeOfFiles

def getListOfAllFiles(_destinationFileShareFolderName, _destinationDirectoryName):
    start_time = datetime.datetime.now()
    rv = False
    file_service = None
    description = ''
    rv, description, file_service, _accountName, _accountKey  = preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
    if (rv == False):
        return rv, description, None
    
    experimentList = list(file_service.list_directories_and_files(_destinationFileShareFolderName, _destinationDirectoryName))
    time_elapsed = datetime.datetime.now() - start_time 
    elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
    
    return True, elapsedTime, experimentList

def isFile(_destinationFileShareFolderName, _destinationDirectoryName, fileName):
    start_time = datetime.datetime.now()
    rv = False
    file_service = None
    description = ''
    rv, description, file_service, _accountName, _accountKey  = preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
    if (rv == False):
        return rv, description, None
    
    rv = file_service.exists(_destinationFileShareFolderName, _destinationDirectoryName, fileName)
    time_elapsed = datetime.datetime.now() - start_time 
    elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
    
    return True, elapsedTime, rv

def createDirectory(_destinationFileShareFolderName, _destinationDirectoryName):
    start_time = datetime.datetime.now()
    rv = False
    file_service = None
    description = ''
    rv, description, file_service, _accountName, _accountKey  = preCheck(_destinationFileShareFolderName, _destinationDirectoryName, False)
    if (rv == False):
        return rv, description, None

    if (file_service.exists(_destinationFileShareFolderName, directory_name=_destinationDirectoryName) == False):
        rv= file_service.create_directory(_destinationFileShareFolderName, _destinationDirectoryName)    

    time_elapsed = datetime.datetime.now() - start_time 
    elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
    
    return True, elapsedTime, rv

def removeAllFiles(_destinationFileShareFolderName, _destinationDirectoryName):
    start_time = datetime.datetime.now()
    rv, desc = deleteAllFiles(_destinationFileShareFolderName, _destinationDirectoryName, None)
    time_elapsed = datetime.datetime.now() - start_time 
    elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
    return True, elapsedTime, rv

def getMaskFileContent(_destinationFileShareFolderName, _destinationDirectoryName):
    start_time = datetime.datetime.now()
    rv, description, file_service, _accountName, _accountKey = preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
    if (rv == False):
        return rv, description, None
    else:
        maskContent = ''
        # check if maskFile exists and load its content
        if (file_service.exists(_destinationFileShareFolderName, _destinationDirectoryName, maskFileName) != False):
            fileMask = file_service.get_file_to_text(_destinationFileShareFolderName, _destinationDirectoryName , maskFileName)
            if (fileMask is not None and fileMask.content is not None and len(fileMask.content) >0 ):
                maskContent = json.loads(fileMask.content)
        time_elapsed = datetime.datetime.now() - start_time 
        elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
        return True, elapsedTime, maskContent

def saveFileImage(_destinationFileShareFolderName, _destinationDirectoryName, fileName, byteArray ):
    start_time = datetime.datetime.now()
    rv, description, file_service, _accountName, _accountKey = preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
    if (rv == False):
        return rv, description, None
    else:
        # create file from the byteArray passed. Will need to check if this can be read back later. 
        # Return value is in the call-back which is not triggered
        file_service.create_file_from_bytes(_destinationFileShareFolderName, _destinationDirectoryName, fileName, byteArray)
        time_elapsed = datetime.datetime.now() - start_time 
        elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
        return True, elapsedTime, 0

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