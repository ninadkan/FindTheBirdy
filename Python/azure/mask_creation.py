#lets create the basic template
# sources
# https://stackoverflow.com/questions/37624509/whats-the-most-efficient-way-to-select-a-non-rectangular-roi-of-an-image-in-ope 
import numpy as np
import cv2
import os
import json
import io

from azureCommon import preCheck

maskFileName = 'mask_file.txt'

def GetMaskedImageImpl(_sourceFileShareFolderName, _sourceDirectoryName, _imageFileName, _maskTags):
    '''
    _sourceDirectoryName : format should be directoryName/secondDirectoryName/

    '''

    # print(_sourceFileShareFolderName)
    # print(_sourceDirectoryName)
    # print(_imageFileName)
    # print(_maskTags)
    rv = False
    rv, description, file_service, _accountName, _accountKey  = preCheck(_sourceFileShareFolderName, _sourceDirectoryName)
    if (rv == False):
        return rv, description
    else: 
        if (file_service.exists(_sourceFileShareFolderName, _sourceDirectoryName, _imageFileName) == False):
            return rv, "Image file does not exist"
        
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
                masks = _maskTags
                # this will override existing file. TOUGH
                #file_service.create_file_from_text(_sourceFileShareFolderName, _sourceDirectoryName, 
                #                                    maskFileName, _maskTags)

        # expectation is that the mask file exists in the source folder
        if (loadFromCloud == True):
            if (file_service.exists(_sourceFileShareFolderName, _sourceDirectoryName, maskFileName) == False):
                return rv, "_maskTags cannot be null as maskImage file also not exist!!!"
            else: 
                fileMask = file_service.get_file_to_text(_sourceFileShareFolderName, _sourceDirectoryName, maskFileName)
                if (fileMask is not None and fileMask.content is not None and len(fileMask.content) >0 ):
                    masks = json.loads(fileMask.content)
                    if not(masks is not None and len(masks) > 0):
                        return rv, "unable to load valid values for mask"
                else:
                    return rv, "Unable to load filemask "
        
        assert(masks is not None and len(masks) > 0), "Mask value not set in logic!!!"
        # load our source file
        output_stream = io.BytesIO()
        fileImage = file_service.get_file_to_stream(_sourceFileShareFolderName, _sourceDirectoryName, 
                                        _imageFileName, output_stream)

        content_length = fileImage.properties.content_length
        #print(content_length)
        if (content_length is not None and content_length > 0):
            output_stream.seek(0)
            file_bytes = np.asarray(bytearray(output_stream.read()), dtype=np.uint8)
            assert(file_bytes is not None), "Unable to decode convert to byteArray" + _imageFileName
            cv2_img = cv2.imdecode(file_bytes, 1 )
            assert(cv2_img is not None), "Unable to decode " + _imageFileName
            colorImage = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
            assert(colorImage is not None), "Unable to load " + _imageFileName

            height, width = colorImage.shape[:2]
            #print("height = {0}, width = {1}".format(str(height), str(width)))

            #colour mask
            colourMask = colorImage[0:height, 0:width]

            #create the masks
            cv2.fillPoly(colourMask, [np.array(masks)],(0,0,0))

            _, _encoded_image = cv2.imencode('.jpg',colourMask)

            return True, _encoded_image #cv2.imencode('.jpg',colourMask)
        else:
            return rv, "Null content obtained from the image source file"
       
           
