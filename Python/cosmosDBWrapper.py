import argparse
# import sys
# sys.path.insert(0, '../') # needed as common is in the parent folder
import common
from cosmosBase import cosmosBase

###############################################################################        

class clsCosmosWrapper(cosmosBase):
    def __init__(self, host='', key='', databaseId=''):
        super().__init__(host=host, key=key, databaseId=databaseId, collectionName=common._COLLECTIONAME )
        self.sprocReadAllExperimentLink = super().getStoredProcLink('returnAllExperimentList')
        assert (self.sprocReadAllExperimentLink is not None)
        return
               
    # -------------------------------------------------------------------------

    def logExperimentResult(self, documentDict, removeExisting=True):
        """
        function to log the result to CosmosDB.
        """
        return self._insert_document_from_dict(documentDict, removeExisting)

    # # -------------------------------------------------------------------------        
    # def returnAllCollection(self):
    #     return super().returnAllCollection()
    # # -------------------------------------------------------------------------
    # def returnAllDocuments(self, collectionLink):
    #     return super().returnAllDocuments(collectionLink)
    # # -------------------------------------------------------------------------
    # def returnDocument(self, documentLink):
    #     '''
    #     documentID contains the completeId
    #     '''
    #     return super().returnDocument(documentLink)
    # -------------------------------------------------------------------------


    def saveLabelledImageListImpl(self, providerId, experimentName, dictObject):
        self._insert_document_in_collection(providerId, experimentName,dictObject)

    # -------------------------------------------------------------------------

    def _insert_document_from_dict(self, dictObject, removeExisting=True):
        assert(dictObject is not None), "dictObject parameter is mandatory!"

        providerId = dictObject[common._IMAGE_DETECTION_PROVIDER_TAG]
        experimentName = dictObject[common._EXPERIMENTNAME_TAG]

        assert(providerId is not None), "providerId parameter is mandatory in Dictionary!"
        assert(experimentName is not None), "experimentName parameter is mandatory in Dictionary!"
        return self._insert_document_in_collection(providerId, experimentName, dictObject, removeExisting)

    # -------------------------------------------------------------------------

    def _insert_document_in_collection(self, providerId, experimentName, dictObject, removeExisting=True):
        '''
        checks for existence of a document, If it exists, deletes it and inserts
        a new record. checks for id as well as experiment name in the document. 
        providerId : Application compatible document Id, providerName
        '''
        if removeExisting == True:
            self._removeExistingDocuments(providerId, experimentName)
                
        return super().createItem(dictObject)
    
    # -------------------------------------------------------------------------

    def _removeExistingDocuments(self,providerId, experimentName):
        docs = self._queryDocsForExistence(providerId, experimentName)
        # remove all the existing document first
        super().removeExistingDocuments(docs)

 
    # -------------------------------------------------------------------------
    def returnLabelledImageListImpl(self, providerId, experimentName):
        return self._queryDocsForExistence(providerId, experimentName)

    # -------------------------------------------------------------------------
    def _queryDocsForExistence(self, providerId, experimentName):
        """
        Finding a unique record inside the collection. 
        """
        selectQuery = "SELECT * FROM r WHERE r." + common._IMAGE_DETECTION_PROVIDER_TAG +  "=@providerId and r." + common._EXPERIMENTNAME_TAG + "=@experimentID"
        documentquery = {
                "query": selectQuery ,
                "parameters": [ { "name":"@providerId", "value": providerId } ,
                                {"name":"@experimentID", "value": experimentName}]
                }
        return super().getDocumentFromQuery(documentquery)

    # -------------------------------------------------------------------------
    def returnAllExperimentResultImpl(self):
        # need to get the sproc_link 
        return super().getClient().ExecuteStoredProcedure(self.sprocReadAllExperimentLink, None)

    # -------------------------------------------------------------------------
    def removeAll(self):
        lst = list(super().getClient().ReadItems(super().getCollectionSelfLink(), {'maxItemCount':300}))
        super().removeExistingDocuments(lst)
        return

    
###############################################################################        
    

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(
    #     description=__doc__,
    #     formatter_class=argparse.RawDescriptionHelpFormatter,
    # )

    # parser = argparse.ArgumentParser(description=__doc__,
    #                 formatter_class=argparse.RawDescriptionHelpFormatter)
    # parser.add_argument("-v", "--verbose", help="increase output verbosity",action="store_true")
    # subparsers = parser.add_subparsers(dest="command")
    # process_parser = subparsers.add_parser("logExperimentResult", help=clsCosmosWrapper.logExperimentResult.__doc__)
    # process_parser.add_argument("host", nargs='?', default='')
    # process_parser.add_argument("key", nargs='?',default='')
    # process_parser.add_argument("databaseId", nargs='?', default='')
   
    # args = parser.parse_args()

    # if (args.verbose):
    #     TRACE_PRINT = True

    # if args.command == "logExperimentResult":    
    #     print("Running experiment")
    #     objRun = clsCosmosWrapper() #(args.host, args.key. args.databaseId)
    #     import datetime
    #     experimentTag = "02/02/2019 12:06"
    #     dictObject = {  
    #                     common._IMAGE_DETECTION_PROVIDER_TAG : common._ID_FOR_USER_DETECTION,
    #                     common._EXPERIMENTNAME_TAG : experimentTag , 
    #                     'id': 'SomeFileName' + "_" + str(datetime.datetime.now()),  # this cannot be a numeric number!!!
    #                     'elapsedTime': "12:10:10",
    #                     'result-totalNumberOfRecords': 1234,
    #                     'result-true_true': 15,
    #                     'result-false_positive': 23,
    #                     'result-false_negative': 2,
    #                     'param-historyImage' : 10, 
    #                     'param-varThreshold' : 25, 
    #                     'param-numberOfIterations' : -1, 
    #                     'param-boundingRectAreaThreshold' : 1000, 
    #                     'param-contourCountThreshold' : 15,
    #                     'param-maskDiffThreshold' : 2,
    #                     'param-partOfFileName' : ''
    #                     }

    #     # test everything is running ok
    #     objRun.returnAllCollection()

    #     # now test the log insertion of the document
    #     objRun.logExperimentResult(dictObject)

    #     # test existence
    #     docs = objRun._queryDocsForExistence(common._ID_FOR_USER_DETECTION, experimentTag)
    #     if (docs is not None):
    #         # found the document, lets remove it
    #         objRun._removeExistingDocuments(common._ID_FOR_USER_DETECTION, experimentTag)
    #         # does it still exist?
    #         docs = objRun._queryDocsForExistence(common._ID_FOR_USER_DETECTION, experimentTag)
    #         if (docs is not None and (len(docs)> 0)):
    #             print("Error, unable to delete the existing row")
    #         else:
    #             print ("OK")
    #     else:
    #         print("Error as the created object was not found")
    # objRun = clsCosmosWrapper()
    # objRun.removeAll()
    pass

    


    
