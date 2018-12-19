#lets create the basic template
# sources
# https://stackoverflow.com/questions/37624509/whats-the-most-efficient-way-to-select-a-non-rectangular-roi-of-an-image-in-ope 
import numpy as np
import cv2
import os
import json
import io

from .azureCommon import preCheck, maskFileName

def GetMaskedImageImpl(_sourceFileShareFolderName, _sourceDirectoryName, _imageFileName, _maskTags):
    '''
    _sourceDirectoryName : format should be directoryName/secondDirectoryName/

    '''
    rv = False
    rv, description, file_service, _accountName, _accountKey  = preCheck(_sourceFileShareFolderName, _sourceDirectoryName)
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
            if (file_service.exists(_sourceFileShareFolderName, _sourceDirectoryName, maskFileName) == False):
                return rv, "_maskTags cannot be null as maskImage file also not exist!!!", None
            else: 
                fileMask = file_service.get_file_to_text(_sourceFileShareFolderName, _sourceDirectoryName, maskFileName)
                if (fileMask is not None and fileMask.content is not None and len(fileMask.content) >0 ):
                    masks = json.loads(fileMask.content)
                    if not(masks is not None and len(masks) > 0):
                        return rv, "unable to load valid values for mask", None
                else:
                    return rv, "Unable to load filemask " , None

        if (masks is not None and len(masks) > 0):
            return GetRawSourceImageImpl(_sourceFileShareFolderName, _sourceDirectoryName, _imageFileName, True, masks)
        else:
            return rv, "Mask value not set in logic!!!", None

def GetRawSourceImageImpl(_sourceFileShareFolderName, _sourceDirectoryName, _imageFileName, loadMask=False, masks=None):
    rv = False
    rv, description, file_service, _accountName, _accountKey  = preCheck(_sourceFileShareFolderName, _sourceDirectoryName)
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


def GetRawImage(_sourceFileShareFolderName, _sourceDirectoryName, _imageFileName):
    rv = False
    rv, description, file_service, _accountName, _accountKey  = preCheck(_sourceFileShareFolderName, _sourceDirectoryName)
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


def GetRawImageAsBytes(_sourceFileShareFolderName, _sourceDirectoryName, _imageFileName):
    rv = False
    rv, description, file_service, _accountName, _accountKey  = preCheck(_sourceFileShareFolderName, _sourceDirectoryName)
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




