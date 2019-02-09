from cosmosBase import clsCosmosOperationsBase
import argparse

import sys
sys.path.insert(0, '../') # needed as common is in the parent folder
import common

###############################################################################
class clsCosmosImageProcessingOperations(clsCosmosOperationsBase):   
    def __init__(self, host='', key='', databaseId=''):
        mandatoryList = [   common._MESSAGE_TYPE_TAG, 
                            common._OPERATIONS_EVENTLOG_TAG, 
                            common._OPERATIONS_CONSUMER_GROUP_TAG, 
                            common._OPERATIONS_PARTITION_ID]
        super().__init__(mandatoryList, common._OPERATIONSCOLLECTIONNAME, host, key, databaseId)
        return
    # -------------------------------------------------------------------------

    def _getDictionaryObjectOffset(self, eventHub, consumerGroup,partition_id, offset, messageType):
        dictObject = {  
                        common._MESSAGE_TYPE_TAG: messageType, 
                        common._OPERATIONS_EVENTLOG_TAG : eventHub,
                        common._OPERATIONS_CONSUMER_GROUP_TAG : consumerGroup , 
                        common._OPERATIONS_PARTITION_ID: partition_id, 
                        common._OPERATIONS_LAST_OFFSET: offset
                    }
        return dictObject   
    # -------------------------------------------------------------------------  

    def _getDictionaryObjectMin(self,eventHub, consumerGroup,partition_id, messageType):
        dictObject = {  
                        common._MESSAGE_TYPE_TAG: messageType, 
                        common._OPERATIONS_EVENTLOG_TAG : eventHub,
                        common._OPERATIONS_CONSUMER_GROUP_TAG : consumerGroup , 
                        common._OPERATIONS_PARTITION_ID: partition_id
                     }
        return dictObject  


    # -------------------------------------------------------------------------

    def insert_offset_document(self, eventHub, consumerGroup,partition_id, offset, messageType, removeExisting=True):
        """
        insert document; All values need to be passed as string
        eventHub, consumerGroup, partitionId and offset, 
        These match the  requirements of the EventHub 
        This method does not allow any additional storage; other option does
        """
        dictObject = self._getDictionaryObjectOffset(eventHub, consumerGroup,partition_id, offset, messageType)
        return self.insert_offset_document_from_dict(dictObject, removeExisting)

    # -------------------------------------------------------------------------

    def insert_offset_document_from_dict(self, dictObject, removeExisting=True):
        assert(dictObject is not None), "dictObject parameter is mandatory!"
        assert(dictObject[common._OPERATIONS_LAST_OFFSET] is not None), "LAST_OFFSET not specified"
        return super().insert_document_in_collection(dictObject, removeExisting)

    # -------------------------------------------------------------------------
    def removeOffsetExistingDocument (self, eventHub, consumerGroup, partition_id, messageType):
        dictObject =  self._getDictionaryObjectMin(eventHub, consumerGroup, partition_id, messageType) 
        self.removeOffsetExistingDocumentDict(dictObject)
        return  

    # -------------------------------------------------------------------------
    def removeOffsetExistingDocumentDict (self, dictObject):
        super().removeExistingDocumentDict(dictObject)
        return      

    # -------------------------------------------------------------------------

    def get_offsetValue(self, eventHub, consumerGroup, partition_id, messageType):
        offset = "-1"
        dictObject =  self._getDictionaryObjectMin(eventHub, consumerGroup, partition_id, messageType) 
        rv = super().getValue(dictObject, common._OPERATIONS_LAST_OFFSET) 
        if (rv is not None):
            offset = rv
        return offset

    # -------------------------------------------------------------------------
    def _queryOffsetDocsForExistence(self, eventHub, consumerGroup, partition_id, messageType):
        dictObject =  self._getDictionaryObjectMin(eventHub, consumerGroup, partition_id, messageType)
        return self._queryOffsetDocsForExistenceWithDictObject(dictObject)


    # -------------------------------------------------------------------------
    def _queryOffsetDocsForExistenceWithDictObject(self, dictObject):
        return super().queryDocsForExistenceWithCheck(dictObject)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser = argparse.ArgumentParser(description=__doc__,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose", help="increase output verbosity",action="store_true")
    subparsers = parser.add_subparsers(dest="command")
    process_parser = subparsers.add_parser("imageOperations", help=clsCosmosImageProcessingOperations.insert_offset_document.__doc__)
    process_parser.add_argument("host", nargs='?', default='')
    process_parser.add_argument("key", nargs='?',default='')
    process_parser.add_argument("databaseId", nargs='?', default='')
   
    args = parser.parse_args()

    if (args.verbose):
        TRACE_PRINT = True

    if args.command == "imageOperations":    
       
        objRun = clsCosmosImageProcessingOperations() 
        import datetime

        eventHub = "evHub"
        consumerGroup = "CGGrp"
        partitionId = "2"
        messageType = common._MESSAGE_TYPE_START_EXPERIMENT
        last_offset = "100"
   
        objRun.insert_offset_document(eventHub, consumerGroup, partitionId, last_offset, messageType )
        offsetValue = objRun.get_offsetValue(eventHub, consumerGroup, partitionId, messageType)
        print (offsetValue)
        print (last_offset)
        assert(offsetValue == last_offset)

        docs = objRun._queryOffsetDocsForExistence(eventHub, consumerGroup, partitionId, messageType)
        objRun.removeOffsetExistingDocument(eventHub, consumerGroup, partitionId, messageType)
        docs = objRun._queryOffsetDocsForExistence(eventHub, consumerGroup, partitionId, messageType)
        assert(len(docs)==0)
