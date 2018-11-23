import os
import sys
from azure.storage.file import FileService

maskFileName = 'mask_file.txt'

def preCheck(_sourceFileShareFolderName, _sourceDirectoryName):
    AZURE_ACN_NAME = 'AZURE_ACN_NAME'
    _accountName = os.environ.get(AZURE_ACN_NAME)
    if (_accountName is None ) or (len(_accountName) == 0):
        return false , 'AZURE_ACN_NAME Environment Variable not set', None, None, None

    AZURE_ACN_STRG_KEY = 'AZURE_ACN_STRG_KEY'
    _accountKey = os.environ.get(AZURE_ACN_STRG_KEY)
    if (_accountKey is None ) or (len(_accountKey) == 0):
        return false , 'AZURE_ACN_STRG_KEY Environment Variable not set', None  , None, None    

    file_service = FileService(account_name=_accountName, account_key=_accountKey)

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
