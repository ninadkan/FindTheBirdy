
import uuid
import sys
sys.path.insert(0, '../') # needed as common is in the parent folder

import common
from cosmosDB.cosmosBase import clsCosmosOperationsBase
import json
import datetime

#import cosmosBase

###############################################################################
class clsStatusUpdate(clsCosmosOperationsBase):   
    def __init__(self, host='', key='', databaseId=''):
        mandatoryList = [   common._OPERATIONS_STATUS_MESSAGE_ID, 
                            common._OPERATIONS_STATUS_EXPERIMENT_NAME,
                            common._OPERATIONS_STATUS_OFFSET]
        super().__init__(mandatoryList, common._OPERATIONSCOLLECTIONNAME, host, key, databaseId)
        self.sprocReadAllMessageIdGroupedLink = super().getStoredProcLink('returnAllMessageIdGroupedList')
        assert (self.sprocReadAllMessageIdGroupedLink is not None)   

        self.sprocGetAllDocsForMsgIdLink = super().getStoredProcLink('getAllDocumentsForMessageId')
        assert (self.sprocGetAllDocsForMsgIdLink is not None)  

        self.sp3Link = super().getStoredProcLink('storedProcedure3')
        assert (self.sp3Link is not None)          
        return

    # -------------------------------------------------------------------------
    def returnAllMessageIdGroupedListImpl(self):
        # need to get the sproc_link 
        assert (self.sprocReadAllMessageIdGroupedLink is not None)      
        lst = super().getClient().ExecuteStoredProcedure(self.sprocReadAllMessageIdGroupedLink, None)
        #print (lst)
        return lst

    # -------------------------------------------------------------------------
    def removeAllDocumentsForSpecificMessageIdImpl(self, messageId):    
        brv = False
        assert (self.sprocGetAllDocsForMsgIdLink is not None) 
        lst = super().getClient().ExecuteStoredProcedure(self.sprocGetAllDocsForMsgIdLink, messageId)
        brv, jsonValue = common.is_json(lst)
        if (brv):
            if (jsonValue is not None):
                result = jsonValue['Result']
                for item in result:
                    itemId = item['id']
                    super().removeExistingDocumentDict({'id':itemId}, True)
        return brv

    # -------------------------------------------------------------------------
    def _getDictionaryObject(self, messageId, experimentName,offset=-1, currentCount=0, maxItems=-1, elapsedTime='', status=''):
        dictObject =    {  
                        common._OPERATIONS_STATUS_MESSAGE_ID : messageId,
                        common._OPERATIONS_STATUS_EXPERIMENT_NAME :experimentName,
                        common._OPERATIONS_STATUS_OFFSET :offset,
                        common._OPERATIONS_STATUS_CURRENT_COUNT :currentCount,
                        common._OPERATIONS_STATUS_MAX_ITEMS :maxItems,
                        common._OPERATIONS_STATUS_ELAPSED_TIME :elapsedTime,
                        common._OPERATIONS_STATUS_STATUS_MESSAGE :status,
                        common._DATETIME_TAG : str(datetime.datetime.now()),
                        }
        return dictObject   
    # -------------------------------------------------------------------------  
    def _getDictionaryObjectMin(self, messageId, experimentName, offset):
        dictObject = {  
                        common._OPERATIONS_STATUS_MESSAGE_ID :messageId,
                        common._OPERATIONS_STATUS_EXPERIMENT_NAME :experimentName,
                        common._OPERATIONS_STATUS_OFFSET :offset,
                      }
        return dictObject  

    # -------------------------------------------------------------------------
    def insert_document(self, messageId, experimentName,offset, currentCount=0, maxItems=-1, elapsedTime='', status='', removeExisting=True):
        """
        insert document; All values need to be passed as string
        eventHub, consumerGroup, partitionId and offset, 
        These match the  requirements of the EventHub 
        This method does not allow any additional data to be passed, passing the dictionary object does
        """
        dictObject = self._getDictionaryObject(messageId, experimentName,offset, currentCount, maxItems, elapsedTime, status)
        return self.insert_document_from_dict(dictObject, removeExisting)

    # -------------------------------------------------------------------------
    def insert_document_from_dict(self, dictObject, removeExisting=True):
        assert(dictObject is not None), "dictObject parameter is mandatory!"
        # Adding updating the Datetime tag into the record. 
        dictObject[common._DATETIME_TAG] = str(datetime.datetime.now())
        return super().insert_document_in_collection(dictObject, removeExisting)

    # -------------------------------------------------------------------------
    def removeExistingDocument (self, messageId, experimentName, offset):
        dictObject =  self._getDictionaryObjectMin(messageId, experimentName, offset)
        self.removeExistingDocumentDict(dictObject)
        return  

    # -------------------------------------------------------------------------
    def removeExistingDocumentDict (self, dictObject):
        super().removeExistingDocumentDict(dictObject)
        return      
    # -------------------------------------------------------------------------
    def get_document_values(self, messageId, experimentName, offset):
        dictObject = None
        doc = self.get_document(messageId, experimentName, offset)
        if doc is not None:
            return  doc[common._OPERATIONS_STATUS_CURRENT_COUNT], doc[common._OPERATIONS_STATUS_MAX_ITEMS], doc[common._OPERATIONS_STATUS_STATUS_MESSAGE]
        else:
            return None, None, None
    # -------------------------------------------------------------------------
    def get_document(self, messageId, experimentName, offset):
        dictObject =  self._getDictionaryObjectMin(messageId, experimentName, offset) 
        return super().getDocument(dictObject)

    # -------------------------------------------------------------------------
    def get_documents(self, messageId, experimentName ):
        dictObject = {  common._OPERATIONS_STATUS_MESSAGE_ID :messageId,
                        common._OPERATIONS_STATUS_EXPERIMENT_NAME :experimentName
                      } 
        return super().getDocuments(dictObject, True) 

    # -------------------------------------------------------------------------   
    def is_operationCompleted(self, messageId, experimentName, numberOfRecordsExpected):
        brv = False
        lst = self.get_documents(messageId, experimentName)
        if (lst is not None):
            if (len(lst) == numberOfRecordsExpected):
                brv = True
                for item in lst:
                    if (int(item[common._OPERATIONS_STATUS_CURRENT_COUNT]) != int(item[common._OPERATIONS_STATUS_MAX_ITEMS])):
                        brv = False # we found one where the match is not correct. 
                        break
        else:
            brv = False
        return brv

    # # -------------------------------------------------------------------------
    # def _queryOffsetDocsForExistence(self, eventHub, consumerGroup, partition_id, messageType):
    #     dictObject =  self._getDictionaryObjectMin(eventHub, consumerGroup, partition_id, messageType)
    #     return self._queryOffsetDocsForExistenceWithDictObject(dictObject)


    # # -------------------------------------------------------------------------
    # def _queryOffsetDocsForExistenceWithDictObject(self, dictObject):
    #     return super().queryDocsForExistenceWithCheck(dictObject)

    # # -------------------------------------------------------------------------
    def oneTimeRemoveAll(self, key, value):
        dictObject = {key:value}
        super().removeExistingDocumentDict(dictObject, True)

    # # -------------------------------------------------------------------------

if __name__ == "__main__":
    objRun = clsStatusUpdate() 
    # parameterObj = [{'inputParameter': 'd57f71e4-1163-4bfc-b3c4-842ce6d6a7eb' }]
    #parameterObj = ['d57f71e4-1163-4bfc-b3c4-842ce6d6a7eb']
    #parameterObj = {'value': 'd57f71e4-1163-4bfc-b3c4-842ce6d6a7eb'}
    #parameterObj = 'd57f71e4-1163-4bfc-b3c4-842ce6d6a7eb'
    #objRun.returnAllMessageIdGroupedListImpl()
    #objRun.removeAllDocumentsForSpecificMessageIdImpl("d57f71e4-1163-4bfc-b3c4-842ce6d6a7eb")
    #objRun.removeAllDocumentsForSpecificMessageId('2d57f71e411634bfcb3c4842ce6d6a7eb')
    #objRun.removeAllDocumentsForSpecificMessageId('2018-04-15')
    #objRun.removeAllDocumentsForSpecificMessageId("22345612344")
    # import datetime


    # messageId = str(uuid.uuid4())
    # experimentName = '2018-04-15'
    # offset=25
    # currentCount=1
    # maxItems=267
    # elapsedTime=datetime.datetime.now().strftime("%c") 
    # status='OK'

    # print("inserting records ....")
    # objRun.insert_document(messageId, experimentName, offset, currentCount, maxItems, elapsedTime, status )
    # print("getting records ....")
    # docs = objRun.get_document(messageId, experimentName, offset)
    # #print(docs)
    # print("getting specific records ....")
    # cnt, mitems, sts = objRun.get_document_values(messageId, experimentName, offset)


    # assert(cnt == currentCount)
    # assert(mitems == maxItems)
    # assert(status == sts)
    # print("get documents...")
    # docs = objRun.get_documents(messageId, experimentName)
    # print(docs)
    # print("removing records ....")
    # objRun.removeExistingDocument(messageId, experimentName, offset)
    # print("getting records ....")
    # docs = objRun.get_document(messageId, experimentName, offset)
    # assert(docs==None)

    # objRun.oneTimeRemoveAll(common._OPERATIONS_STATUS_EXPERIMENT_NAME, experimentName )
    # objRun.oneTimeRemoveAll(common._OPERATIONS_CONSUMER_GROUP_TAG, 'opencv')
    # objRun.oneTimeRemoveAll(common._OPERATIONS_STATUS_MESSAGE_ID, '400b668e-2cd2-4324-8eef-74c161ee9586' )
    
    # objRun.oneTimeRemoveAll(common._MESSAGE_TYPE_TAG, common._MESSAGE_TYPE_DETECTOR_GOOGLE )
    # objRun.oneTimeRemoveAll(common._MESSAGE_TYPE_TAG, common._MESSAGE_TYPE_DETECTOR_AZURE )
    # objRun.oneTimeRemoveAll(common._MESSAGE_TYPE_TAG, common._MESSAGE_TYPE_DETECTOR_YOLO )
    # objRun.oneTimeRemoveAll(common._MESSAGE_TYPE_TAG, common._MESSAGE_TYPE_DETECTOR_MOBILE_NET )
    # objRun.oneTimeRemoveAll(common._MESSAGE_TYPE_TAG, common._MESSAGE_TYPE_DETECTOR_TENSORFLOW )
    # objRun.oneTimeRemoveAll(common._MESSAGE_TYPE_TAG, common._MESSAGE_TYPE_PROCESS_EXPERIMENT )
    # objRun.oneTimeRemoveAll(common._MESSAGE_TYPE_TAG, common._MESSAGE_TYPE_START_EXPERIMENT )
    # objRun.oneTimeRemoveAll(common._MESSAGE_TYPE_TAG, common._MESSAGE_TYPE_DETECTOR_GOOGLE )



