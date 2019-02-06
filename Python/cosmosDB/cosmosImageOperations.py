from cosmosBase import cosmosBase
import argparse

import sys
sys.path.insert(0, '../') # needed as common is in the parent folder
import common

class clsCosmosImageProcessingOperations(cosmosBase):   
    def __init__(self, host='', key='', databaseId=''):
        super().__init__(host, key, databaseId, common._OPERATIONSCOLLECTIONNAME)
        return

    # -------------------------------------------------------------------------

    def insert_document(self, eventHub, consumerGroup,partition_id, offset, messageType, removeExisting=True):
        """
        insert document; All values need to be passed as string
        eventHub, consumerGroup, partitionId and offset, 
        These match the  requirements of the EventHub 
        This method does not allow any additional storage; other option does
        """
        dictObject = {  
                    common._MESSAGE_TYPE_TAG: messageType, 
                    common._OPERATIONS_EVENTLOG_TAG : eventHub,
                    common._OPERATIONS_CONSUMER_GROUP_TAG : consumerGroup , 
                    common._OPERATIONS_PARTITION_ID: partition_id, 
                    common._OPERATIONS_LAST_OFFSET: offset
                    }
        return self.insert_document_from_dict(dictObject, removeExisting)

    # -------------------------------------------------------------------------

    def insert_document_from_dict(self, dictObject, removeExisting=True):
        assert(dictObject is not None), "dictObject parameter is mandatory!"
        assert(dictObject[common._MESSAGE_TYPE_TAG] is not None), "Message Type is not specified"
        assert(dictObject[common._OPERATIONS_EVENTLOG_TAG] is not None), "EVENTLOG_TAG not specified"
        assert(dictObject[common._OPERATIONS_CONSUMER_GROUP_TAG] is not None), "CONSUMER_GROUP_TAG not specified"
        assert(dictObject[common._OPERATIONS_PARTITION_ID] is not None), "PARTITION_ID_TAG not specified"
        assert(dictObject[common._OPERATIONS_LAST_OFFSET] is not None), "LAST_OFFSET not specified"

        return self._insert_document_in_collection(dictObject, removeExisting)

    # -------------------------------------------------------------------------

    def _insert_document_in_collection(self, dictObject, removeExisting=True):
        '''
        checks for existence of a document, If it exists, deletes it and inserts
        a new record. checks for id as well as experiment name in the document. 
        providerId : Application compatible document Id, providerName
        '''
        if removeExisting == True:
            super().removeExistingDocuments(self._queryDocsForExistenceWithDictObject(dictObject))
        return super().createItem(dictObject)
    

    # -------------------------------------------------------------------------
    def removeExistingDocument (self, dictObject):
        super().removeExistingDocuments(self._queryDocsForExistenceWithDictObject(dictObject))
        return      

    # -------------------------------------------------------------------------
    def removeExistingDocument (self, eventHub, consumerGroup, partition_id, messageType):
        dictObject =    { 
                        common._OPERATIONS_EVENTLOG_TAG : eventHub,
                        common._OPERATIONS_CONSUMER_GROUP_TAG : consumerGroup , 
                        common._OPERATIONS_PARTITION_ID: partition_id,
                        common._MESSAGE_TYPE_TAG :  messageType
                        }

        super().removeExistingDocuments(self._queryDocsForExistenceWithDictObject(dictObject))
        return  
    # -------------------------------------------------------------------------

    def get_offsetValue(self, eventHub, consumerGroup, partition_id, messageType):
        offset = "-1"
        docs = self._queryDocsForExistence(eventHub, consumerGroup, partition_id, messageType)
        if (docs is not None and len(docs) > 0):
            firstItem = docs[0]
            offset = firstItem[common._OPERATIONS_LAST_OFFSET]
        return offset

    # -------------------------------------------------------------------------

    def _queryDocsForExistenceWithDictObject(self, dictObject):
        """
        Finding a unique record inside the collection. 
        """
        return self._queryDocsForExistence( dictObject[common._OPERATIONS_EVENTLOG_TAG], 
                                            dictObject[common._OPERATIONS_CONSUMER_GROUP_TAG],
                                            dictObject[ common._OPERATIONS_PARTITION_ID],
                                            dictObject[common._MESSAGE_TYPE_TAG],)

    # -------------------------------------------------------------------------


    def _queryDocsForExistence(self, eventLog, consumerGroup, partitionID, messageType):
        """
        Finding a unique record inside the collection. 
        """
        selectQuery = "SELECT * FROM r WHERE r." + common._OPERATIONS_EVENTLOG_TAG +  "=@eventLog and r." \
                        + common._OPERATIONS_CONSUMER_GROUP_TAG + "=@consumerGroup and r." \
                        + common._OPERATIONS_PARTITION_ID + "=@partitionId and r." \
                        + common._MESSAGE_TYPE_TAG +  "=@messageType"
        documentquery = {
                "query": selectQuery ,
                "parameters": [ { "name":"@eventLog", "value": eventLog } ,
                                {"name":"@consumerGroup", "value": consumerGroup},
                                { "name":"@partitionId", "value": partitionID },
                                {"name":"@messageType", "value": messageType}]
                }
        return super().getDocumentFromQuery(documentquery)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser = argparse.ArgumentParser(description=__doc__,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose", help="increase output verbosity",action="store_true")
    subparsers = parser.add_subparsers(dest="command")
    process_parser = subparsers.add_parser("imageOperations", help=clsCosmosImageProcessingOperations.insert_document.__doc__)
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
   
        objRun.insert_document(eventHub, consumerGroup, partitionId, last_offset, messageType )
        offsetValue = objRun.get_offsetValue(eventHub, consumerGroup, partitionId, messageType)
        print (offsetValue)
        print (last_offset)
        assert(offsetValue == last_offset)

        objRun.removeExistingDocuments(objRun._queryDocsForExistence(eventHub, consumerGroup, partitionId, messageType))
        docs = objRun._queryDocsForExistence(eventHub, consumerGroup, partitionId, messageType)
        assert(len(docs)==0)
