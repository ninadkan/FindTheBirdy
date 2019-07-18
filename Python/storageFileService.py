import io
import os
import time
import sys
from azure.storage.file import FileService
import json
import datetime

import numpy as np
import cv2

import logging
from loggingBase import clsLoggingBase


class storageFileService(clsLoggingBase):
    """
    This class wraps the Blob storage. Should be created in two phases. First passing the 
    account name and second passing the accountkey from the KeyVault. After this the service 
    object is created and can be used to access the blob items 
    """

    def __init__(self, account_name):
        super().__init__(__name__)
        self.account_name=account_name
        self.account_key=None 
        self.service = None
        self.maskFileName = 'mask_file.txt'
        return

    def set_storageKey(self,storageKey):
        self.account_key=storageKey
        if (self.account_name):
            self.service = FileService(account_name= self.account_name, account_key=self.account_key)
        return
    
    def preCheck(self, _sourceFileShareFolderName, _sourceDirectoryName, AdditionalCheck=True):
        super().getLoggingObj().debug('preCheck')
        if (self.service == None):
            if ((self.account_name is None) or len(self.account_name) == 0):
                AZURE_ACN_NAME = 'AZURE_ACN_NAME'
                self.account_name = os.environ.get(AZURE_ACN_NAME)
                if (self.account_name is None ) or (len(self.account_name) == 0):
                    return False , 'AZURE_ACN_NAME Environment Variable not set', None, None, None

            if ((self.account_key is None) or len(self.account_key) == 0):
                AZURE_ACN_STRG_KEY = 'AZURE_ACN_STRG_KEY'
                self.account_key = os.environ.get(AZURE_ACN_STRG_KEY)
                if (self.account_key is None ) or (len(self.account_key) == 0):
                    return False , 'AZURE_ACN_STRG_KEY Environment Variable not set', None  , None, None

            self.service = FileService(account_name=self.account_name, account_key=self.account_key)

            # Can we create file_share service
            if (self.service is None):
                return False, "Unable to create File share, check Account Name, Key and connectivity", None, None, None

        if (AdditionalCheck == True):
            # check for existence of Source share folder
            if (self.service.exists(_sourceFileShareFolderName) == False):
                return False, "source share does not exist", None, None, None

            # check for existence of source share directory 
            if (self.service.exists(_sourceFileShareFolderName, directory_name=_sourceDirectoryName) == False):
                return False, "source directory does not exist", None, None, None

        return True, "OK", self.service, self.account_name, self.account_key

    def CopySourceDestinationImpl(self, _sourceFileShareFolderName, _sourceDirectoryName, 
                                _destinationFileShareFolderName, _destinationDirectoryName, 
                                _ExperimentName, _fileExtensionFilter='.jpg'):
        '''
        This method copies raw data from the source directory to the experiment folder
        _sourceDirectoryName, _destinationDirectoryName: format should be directoryName/secondDirectoryName, no trailing 
        slashes.  
        '''
        
        start_time = datetime.datetime.now()
        rv, description, file_service, _accountName, _accountKey  = self.preCheck(_sourceFileShareFolderName, _sourceDirectoryName)
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

    def GetAllExperimentsWithMaskAndImageFileImpl(self, _destinationFileShareFolderName, _destinationDirectoryName, _fileExtensionFilter='.jpg'):
        rv, description, file_service, _accountName, _accountKey = self.preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
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
                            if (file_service.exists(_destinationFileShareFolderName, _destinationDirectoryName+ "/" + experimentName.name, self.maskFileName) != False):
                                #print(_destinationFileShareFolderName + "/" + _destinationDirectoryName+ "/" + experimentName.name + "/" + self.maskFileName)
                                fileMask = file_service.get_file_to_text(_destinationFileShareFolderName, _destinationDirectoryName+ "/" + experimentName.name, self.maskFileName)
                                if (fileMask is not None and fileMask.content is not None and len(fileMask.content) >0 ):
                                    #print("load content")
                                    maskContent = json.loads(fileMask.content)
                            # load name of first file with extsnsion = _fileExtensionFilter
                            if (filenameList.name.endswith(_fileExtensionFilter)):
                                myVar = {"experimentName":experimentName.name, "filename":filenameList.name, "maskContent": maskContent}
                                returnList.append(myVar)
                                # we've got our file, lets exit from this inner loop
                                break

        return True, returnList

    def SaveMaskFileDataImpl(self, _sourceFileShareFolderName, _sourceDirectoryName, _maskTags):
        start_time = datetime.datetime.now()
        rv = False
        rv, description, file_service, _accountName, _accountKey  = self.preCheck(_sourceFileShareFolderName, _sourceDirectoryName)
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
                        file_service.create_file_from_text(_sourceFileShareFolderName, _sourceDirectoryName, self.maskFileName, _maskTags)
                        time_elapsed = datetime.datetime.now() - start_time 
                        elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
                        return True, elapsedTime
                else:
                    return rv, "masks passed cannot be converted to json objects"

    def GetAllExperimentsFilesNotCopiedImpl(self, _destinationFileShareFolderName, _destinationDirectoryName, _experimentNames):
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
        rv, description, file_service, _accountName, _accountKey  = self.preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
        if (rv == False):
            return rv, description, None
        
        returnList = []

        for experimentName in (_experimentNames):
            if (file_service.exists(_destinationFileShareFolderName, _destinationDirectoryName+ "/" + experimentName) == False):
                returnList.append(experimentName)

        time_elapsed = datetime.datetime.now() - start_time 
        elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
        return True, elapsedTime, returnList

    def TestGetAllExperimentNames(self, _destinationFileShareFolderName, _destinationDirectoryName):
        start_time = datetime.datetime.now()
        rv, description, file_service, _accountName, _accountKey = self.preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
        if (rv == False):
            return rv, description, None
        else:
            experimentList = list(file_service.list_directories_and_files(_destinationFileShareFolderName, directory_name=_destinationDirectoryName))
            time_elapsed = datetime.datetime.now() - start_time 
            elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
            return True, elapsedTime, experimentList

    def GetAllSourceUniqueExperimentNamesImpl(self, _sourceFileShareFolderName, _sourceDirectoryName, _fileExtensionFilter='.jpg'):
        '''
        This function is to be used @ the source folder, where the images are all clubbed together. and we want to extract out 
        the various experiment names that have been created. 
        In our context the _sourceFileShareFolderName = 'linuxraspshare' and '_sourceDirectoryName' = 'Share'
        '''
        start_time = datetime.datetime.now()
        rv = False
        rv, description, file_service, _accountName, _accountKey  = self.preCheck(_sourceFileShareFolderName, _sourceDirectoryName)
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

    def GetAllDestinationExperimentsWhereMaskFileNotPresentImpl(self, _destinationFileShareFolderName, _destinationDirectoryName, _experimentNames):
        '''
        _experimentNames contains list of all the experiment names. 
        This function looks for existence of mask file under the destination folders and if it does not exists, marks that experiment 
        as not yet processed and returns that as part of the list. If the mask file exists under the destination folder, it is assumed 
        that the masking exercise has been done for that experiment
        '''
        start_time = datetime.datetime.now()
        rv = False
        rv, description, file_service, _accountName, _accountKey  = self.preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
        if (rv == False):
            return rv, description, None
        
        returnList = []

        for experimentName in (_experimentNames):
            # check if maskFile exists and load its content
            if (file_service.exists(_destinationFileShareFolderName, _destinationDirectoryName+ "/" + experimentName, self.maskFileName) == False):
                returnList.append(experimentName)

        time_elapsed = datetime.datetime.now() - start_time 
        elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
        return True, elapsedTime, returnList

    def GetAllDestinationUniqueExperimentNamesImpl(self, _destinationFileShareFolderName, _destinationDirectoryName):
        '''
        This function returns the number of folders that currently exists under the destination folders. 
        _destinationFileShareFolderName = 'experiment'
        _destinationDirectoryName = 'object-detection'
        '''
        start_time = datetime.datetime.now()
        rv = False
        rv, description, file_service, _accountName, _accountKey  = self.preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
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

    def GetAllDestinationExperimentNamesWithOutputFilesImpl(self, 
                                                                _destinationFileShareFolderName, 
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
        rv, description, file_service, _accountName, _accountKey  = self.preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
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

    def deleteAllFiles(self, _sourceFileShareFolderName, _sourceDirectoryName, _fileExtensionFilter='.jpg' ):
        rv, description, file_service, _accountName, _accountKey = self.preCheck(_sourceFileShareFolderName, _sourceDirectoryName)
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

    def DashBoardGetAllFilesInfoImpl(   self, 
                                        _sourceFileShareFolderName, 
                                        _sourceDirectoryNameList,
                                        _destinationFileShareFolderName, 
                                        _destinationDirectoryName,
                                        _outputFolderName = 'output', 
                                        _fileExtensionFilter='.jpg'):
        '''
        Mother of all functions and scans through each and every file and returns lots of information. Could take up-to 40+ minutes to run
        ''' 
        start_time = datetime.datetime.now()  
        print('phase1')
        result, description, returnSourceDict = self.DashBoardGetAllSourceFilesInfoImpl(_sourceFileShareFolderName, _sourceDirectoryNameList, _fileExtensionFilter) 
        if (result == True):
            print('phase2')
            result, description, returnDestinationDict = self.DashBoardGetAllDestinationFilesInfoImpl(
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
                
                return self.returnFormattedValue(start_time, True, "OK", combinedDict)
            else:
                return self.returnFormattedValue(start_time, result, description, None)
        else:
            self.returnFormattedValue(start_time, result, description, None)

    def DashBoardGetAllSourceFilesInfoImplWrapper(self, _sourceFileShareFolderName, _sourceDirectoryNameList, _fileExtensionFilter='.jpg'):
        start_time = datetime.datetime.now()
        result, description, returnDict = self.DashBoardGetAllSourceFilesInfoImpl(_sourceFileShareFolderName, _sourceDirectoryNameList, _fileExtensionFilter)
        return self.returnFormattedValue(start_time, result, description, returnDict)

    def DashBoardGetAllSourceFilesInfoImpl(self, _sourceFileShareFolderName, _sourceDirectoryNameList, _fileExtensionFilter='.jpg'):
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
        rv, description, file_service, _accountName, _accountKey  = self.preCheck(_sourceFileShareFolderName, _sourceDirectoryNameList[0])
        if (rv == False):
            return rv, description, None
        returnDict = dict()

        for _sourceDirectoryName in _sourceDirectoryNameList:
            #print(_sourceDirectoryName)
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

    def DashBoardGetAllDestinationFilesInfoImplWrapper( self, 
                                                        _destinationFileShareFolderName, 
                                                        _destinationDirectoryName,
                                                        _outputFolderName = 'output',
                                                        _fileExtensionFilter='.jpg',
                                                        _returnDict = None,
                                                        _file_service = None):
        start_time = datetime.datetime.now()
        result, description, returnDict = self.DashBoardGetAllDestinationFilesInfoImpl( _destinationFileShareFolderName, 
                                                                                    _destinationDirectoryName,
                                                                                    _outputFolderName ,
                                                                                    _fileExtensionFilter,
                                                                                    _returnDict )

        return self.returnFormattedValue(start_time, result, description, returnDict)

    def DashBoardGetAllDestinationFilesInfoImpl(self, 
                                                _destinationFileShareFolderName, 
                                                _destinationDirectoryName,
                                                _outputFolderName = 'output',
                                                _fileExtensionFilter='.jpg',
                                                _returnDict = None):
        start_time = datetime.datetime.now()
        print(start_time)
        rv = False
        file_service = None
        description = ''
        rv, description, file_service, _accountName, _accountKey  = self.preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
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
        # print("1st pass done")

        # maxIteration = 3
        # startIteration = 0


        for key in returnDict:
            print(key)

            
            # if (startIteration > maxIteration ):
            #     break
            # else:
            #     startIteration += 1

            combinedFolderName = _destinationDirectoryName+"/"+ key
            if (file_service.exists(_destinationFileShareFolderName,combinedFolderName, self.maskFileName)):
                if _returnDict is None:
                    returnDict[key][0] = 0
                    returnDict[key][1] = 0
                
                returnDict[key][2] = True
                numberOfFiles , sizeOfFiles =  self.getNumberOfFilesAndFileSize(file_service,_destinationFileShareFolderName, combinedFolderName , _fileExtensionFilter )
                returnDict[key][3] = numberOfFiles
                returnDict[key][4] = sizeOfFiles
                combinedFolderName = _destinationDirectoryName+"/"+ key + "/" + _outputFolderName
                if (file_service.exists(_destinationFileShareFolderName,combinedFolderName)):
                    returnDict[key][5] = True
                    numberOfFiles , sizeOfFiles =  self.getNumberOfFilesAndFileSize(file_service, _destinationFileShareFolderName, combinedFolderName, _fileExtensionFilter )
                    returnDict[key][6] = numberOfFiles
                    returnDict[key][7] = sizeOfFiles
        
        return True, "OK", returnDict

    def returnFormattedValue(self, start_time, result, description, returnDict):
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

    def getNumberOfFilesAndFileSize(self, file_service, shareFolder, directoryName, _fileExtensionFilter):
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

    def getListOfAllFiles(self, _destinationFileShareFolderName, _destinationDirectoryName):
        start_time = datetime.datetime.now()
        rv = False
        file_service = None
        description = ''
        rv, description, file_service, _accountName, _accountKey  = self.preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
        if (rv == False):
            return rv, description, None
        
        experimentList = list(file_service.list_directories_and_files(_destinationFileShareFolderName, _destinationDirectoryName))
        time_elapsed = datetime.datetime.now() - start_time 
        elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
        
        return True, elapsedTime, experimentList

    def isFile(self, _destinationFileShareFolderName, _destinationDirectoryName, fileName):
        start_time = datetime.datetime.now()
        rv = False
        file_service = None
        description = ''
        rv, description, file_service, _accountName, _accountKey  = self.preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
        if (rv == False):
            return rv, description, None
        
        rv = file_service.exists(_destinationFileShareFolderName, _destinationDirectoryName, fileName)
        time_elapsed = datetime.datetime.now() - start_time 
        elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
        
        return True, elapsedTime, rv

    def createDirectory(self, _destinationFileShareFolderName, _destinationDirectoryName):
        start_time = datetime.datetime.now()
        rv = False
        file_service = None
        description = ''
        rv, description, file_service, _accountName, _accountKey  = self.preCheck(_destinationFileShareFolderName, _destinationDirectoryName, False)
        if (rv == False):
            return rv, description, None

        if (file_service.exists(_destinationFileShareFolderName, directory_name=_destinationDirectoryName) == False):
            print(_accountName)
            print(_accountKey)
            print (_destinationFileShareFolderName)
            print(_destinationDirectoryName)
            rv= file_service.create_directory(_destinationFileShareFolderName, _destinationDirectoryName)    

        time_elapsed = datetime.datetime.now() - start_time 
        elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
        
        return True, elapsedTime, rv

    def removeAllFiles(self, _destinationFileShareFolderName, _destinationDirectoryName):
        start_time = datetime.datetime.now()
        rv, desc = self.deleteAllFiles(_destinationFileShareFolderName, _destinationDirectoryName, None)
        time_elapsed = datetime.datetime.now() - start_time 
        elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
        return True, elapsedTime, rv

    def getMaskFileContent(self, _destinationFileShareFolderName, _destinationDirectoryName):
        start_time = datetime.datetime.now()
        rv, description, file_service, _accountName, _accountKey = self.preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
        if (rv == False):
            return rv, description, None
        else:
            maskContent = ''
            # check if maskFile exists and load its content
            if (file_service.exists(_destinationFileShareFolderName, _destinationDirectoryName, self.maskFileName) != False):
                fileMask = file_service.get_file_to_text(_destinationFileShareFolderName, _destinationDirectoryName , self.maskFileName)
                if (fileMask is not None and fileMask.content is not None and len(fileMask.content) >0 ):
                    maskContent = json.loads(fileMask.content)
            time_elapsed = datetime.datetime.now() - start_time 
            elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
            return True, elapsedTime, maskContent

    def saveFileImage(self, _destinationFileShareFolderName, _destinationDirectoryName, fileName, byteArray ):
        start_time = datetime.datetime.now()
        rv, description, file_service, _accountName, _accountKey = self.preCheck(_destinationFileShareFolderName, _destinationDirectoryName)
        if (rv == False):
            return rv, description, None
        else:
            # create file from the byteArray passed. Will need to check if this can be read back later. 
            # Return value is in the call-back which is not triggered
            file_service.create_file_from_bytes(_destinationFileShareFolderName, _destinationDirectoryName, fileName, byteArray)
            time_elapsed = datetime.datetime.now() - start_time 
            elapsedTime = "{}:{}".format(time_elapsed.seconds, time_elapsed.microseconds)
            return True, elapsedTime, 0

    # masked file implementations
    def GetMaskedImageImpl(self, _sourceFileShareFolderName, _sourceDirectoryName, _imageFileName, _maskTags):
        '''
        _sourceDirectoryName : format should be directoryName/secondDirectoryName/

        '''
        rv = False
        rv, description, file_service, _accountName, _accountKey  = self.preCheck(_sourceFileShareFolderName, _sourceDirectoryName)
        if (rv == False):
            return rv, description, None
        else: 
            masks = []
            # more validations
            loadFromCloud = False
            if (_maskTags is None):
                loadFromCloud = True
            else:
                # try to load the masks to a temporary objectt
                if (len(_maskTags) == 0):
                    loadFromCloud = True
                else:
                    masks = json.loads(_maskTags)
                    
    
            # expectation is that the mask file exists in the source folder
            if (loadFromCloud == True):
                print('loadFromCloud')
                if (file_service.exists(_sourceFileShareFolderName, _sourceDirectoryName, self.maskFileName) == False):
                    return rv, "_maskTags cannot be null as maskImage file also not exist!!!", None
                else: 
                    fileMask = file_service.get_file_to_text(_sourceFileShareFolderName, _sourceDirectoryName, self.maskFileName)
                    if (fileMask is not None and fileMask.content is not None and len(fileMask.content) >0 ):
                        masks = json.loads(fileMask.content)
                        if not(masks is not None and len(masks) > 0):
                            return rv, "unable to load valid values for mask", None
                    else:
                        return rv, "Unable to load filemask " , None

            if (masks is not None and len(masks) > 0):
                return self.GetRawSourceImageImpl(_sourceFileShareFolderName, _sourceDirectoryName, _imageFileName, True, masks)
            else:
                return rv, "Mask value not set in logic!!!", None

    def GetRawSourceImageImpl(self, _sourceFileShareFolderName, _sourceDirectoryName, _imageFileName, loadMask=False, masks=None):
        rv = False
        rv, description, file_service, _accountName, _accountKey  = self.preCheck(_sourceFileShareFolderName, _sourceDirectoryName)
        if (rv == False):
            return rv, description, None
        else: 
            if (file_service.exists(_sourceFileShareFolderName, _sourceDirectoryName, _imageFileName) == False):
                return rv, "Image file does not exist", None
            else:
                # load our source file
                output_stream = io.BytesIO()
                fileImage = file_service.get_file_to_stream(_sourceFileShareFolderName, _sourceDirectoryName, 
                                                _imageFileName, output_stream)

                content_length = fileImage.properties.content_length
                if (content_length is not None and content_length > 0):
                    output_stream.seek(0)
                    file_bytes = np.asarray(bytearray(output_stream.read()), dtype=np.uint8)
                    if (file_bytes is not None):
                        cv2_img = cv2.imdecode(file_bytes, 1 ) # don't know what 1 does but it sorta works
                        if (cv2_img is not None) :
                            colorImage = cv2.cvtColor(cv2_img, cv2.COLOR_RGB2BGR) #TODO Not sure this is needed, COLOR_BGR2RGB or might be reversing the image
                            if (colorImage is not None):
                                height, width = colorImage.shape[:2]
                                colourMask = colorImage[0:height, 0:width]
                                if (loadMask == True):
                                    cv2.fillPoly(colourMask, [np.array(masks)],(0,0,0))
                                _, _encoded_image = cv2.imencode('.jpg',colourMask)
                                return True, "OK", _encoded_image #cv2.imencode('.jpg',colourMask)                        
                            else:
                                return rv, "Unable to convert image to COLOR_BGR2RGB :" + _imageFileName, None
                        else:
                            return rv, "Unable to decode : " + _imageFileName, None
                    else :
                        return rv, "Unable to decode convert to byteArray :" + _imageFileName, None
                else:
                    return rv, "Null content obtained from the image source file", None


    def GetRawImage(self, _sourceFileShareFolderName, _sourceDirectoryName, _imageFileName):
        rv = False
        rv, description, file_service, _accountName, _accountKey  = self.preCheck(_sourceFileShareFolderName, _sourceDirectoryName)
        if (rv == False):
            return rv, description, None
        else: 
            if (file_service.exists(_sourceFileShareFolderName, _sourceDirectoryName, _imageFileName) == False):
                return rv, "Image file does not exist", None
            else:
                # load our source file
                output_stream = io.BytesIO()
                fileImage = file_service.get_file_to_stream(_sourceFileShareFolderName, _sourceDirectoryName, 
                                                _imageFileName, output_stream)

                content_length = fileImage.properties.content_length
                if (content_length is not None and content_length > 0):
                    output_stream.seek(0)
                    file_bytes = np.asarray(bytearray(output_stream.read()), dtype=np.uint8)
                    if (file_bytes is not None):
                        cv2_img = cv2.imdecode(file_bytes, 1 )
                        if (cv2_img is not None) :
                            return True, "OK", cv2_img #cv2.imencode('.jpg',colourMask)                        
                        else:
                            return rv, "Unable to decode : " + _imageFileName, None
                    else :
                        return rv, "Unable to decode convert to byteArray :" + _imageFileName, None
                else:
                    return rv, "Null content obtained from the image source file", None


    def GetRawImageAsBytes(self, _sourceFileShareFolderName, _sourceDirectoryName, _imageFileName):
        rv = False
        rv, description, file_service, _accountName, _accountKey  = self.preCheck(_sourceFileShareFolderName, _sourceDirectoryName)
        if (rv == False):
            return rv, description, None
        else: 
            if (file_service.exists(_sourceFileShareFolderName, _sourceDirectoryName, _imageFileName) == False):
                return rv, "Image file does not exist", None
            else:
                # load our source file
                output_stream = io.BytesIO()
                fileImage = file_service.get_file_to_stream(_sourceFileShareFolderName, _sourceDirectoryName, 
                                                _imageFileName, output_stream)
                content_length = fileImage.properties.content_length
                if (content_length is not None and content_length > 0):
                    output_stream.seek(0)
                    file_bytes = output_stream.read()
                    if (file_bytes is not None):
                        return True, "OK", file_bytes             
                    else :
                        return rv, "Unable to get byte byteArray :" + _imageFileName, None
                else:
                    return rv, "Null content obtained from the image source file", None


if __name__ == "__main__":
    CopySourceDestination('linuxraspshare', 'Share', 'experiment-data', 'object-detection', '2018-11-09_')





   

