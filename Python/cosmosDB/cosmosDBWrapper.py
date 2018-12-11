# this file  wraps CosmosDB API in python
# https://github.com/Azure/azure-cosmos-python
# https://github.com/Azure/azure-cosmos-python # MOST IMPRTANT AND UPDATED SITE
# https://docs.microsoft.com/en-gb/python/api/overview/azure/cosmosdb?view=azure-python
# pip install pydocumentdb
# pip install azure-mgmt-cosmosdb
# https://docs.microsoft.com/en-us/azure/cosmos-db/sql-api-sdk-python
# https://github.com/Azure/azure-cosmos-python/blob/d78170214467e3ab71ace1a7400f5a7fa5a7b5b0/samples/DatabaseManagement/Program.py#L65-L76
# https://docs.microsoft.com/en-us/python/api/overview/azure/cosmosdb?view=azure-python
# 
# Prerequistes - 
# 
# 1. An Azure DocumentDB account - 
#    https:#azure.microsoft.com/en-us/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure DocumentDB PyPi package - 
#    https://pypi.python.org/pypi/pydocumentdb/


# ensure that you've installed PyPI
# challenge: documentation says that the python version supported is 3.5
# we are playing with version 3.6!!!
# let's see what happens
# pip install azure-cosmos, sort of works!!! 



#import pydocumentdb.document_client as document_client
import azure.cosmos.cosmos_client as document_client
import azure.cosmos.errors as errors
import argparse

import sys
sys.path.insert(0, '../')
import common
#from pydocumentdb import document_client
# import cosmosDatabaseManagement as dbMgmt 
# import cosmosCollectionManagement as collMgmt 
# import cosmosDocumentManagement as docMgmt 

# from cosmosDocumentManagement import DocumentManagement as docMgmt 
# document_client.CosmosClient.


def ifNullReadAndAssignFromEnviron(variableName, KEY):
    import os
    if (variableName is None) or (len(variableName) == 0 ):
        variableName = os.environ.get(KEY)
    return variableName

class clsCosmosWrapper:

    def __init__(self, host='', key='', databaseId=''):
        self.COLLECTIONAME = common._COLLECTIONAME
        
        self.ID_FOR_USER_DETECTION = common._ID_FOR_USER_DETECTION
        self.DETECTED_IMAGES_TAG = common._DETECTED_IMAGES_TAG
        
        self.EXPERIMENTNAME = common._EXPERIMENTNAME_TAG
        self.IMAGE_DETECTION_PROVIDER = common._IMAGE_DETECTION_PROVIDER_TAG
        
        self.host = ifNullReadAndAssignFromEnviron(host, 'COSMOSDB_HOST')
        assert(self.host is not None), "cosmosDB host not specified"
        self.key =  ifNullReadAndAssignFromEnviron(key, 'COSMOSDB_KEY')
        assert(self.key is not None), "cosmosDB key is not specified"
        self.databaseId =  ifNullReadAndAssignFromEnviron(databaseId, 'COSMOSDB_DATABASE')
        assert(self.databaseId is not None), "cosmosDB database is not specified"

        # create our client object
        hostFormat = "https://{0}.documents.azure.com:443/".format(self.host)
        self.client = document_client.CosmosClient(  hostFormat , 
                                                        {'masterKey': self.key})
        assert(self.client is not None), "Unable to create client"
        #Check existence of database and create it it does not exist
        self.dbSelfLink = None
        #print("Querying database...")
        databases = list(self.client.QueryDatabases({
            "query": "SELECT * FROM r WHERE r.id=@id",
            "parameters": [
                { "name":"@id", "value": self.databaseId }
            ] }))
        if len(databases) > 0: # exists, take the first one, it should return only one
            #print("Database found...")
            self.dbSelfLink = databases[0]['_self'] 
        else:
            print("Creating database ...")
            self.dbSelfLink = self.client.CreateDatabase({"id": self.databaseId})['_self']
        assert (self.dbSelfLink is not None)
        
        self.collectionLink = None
        # find if any containers exist
        collections = list(self.client.QueryContainers( self.dbSelfLink,
            {"query": "SELECT * FROM r WHERE r.id=@id", "parameters": 
            [{ "name":"@id", "value": self.COLLECTIONAME }]}))
        if len(collections) > 0:
            self.collectionLink = collections[0]['_self'] # take the first item
        else:
            self.collectionLink = self.client.CreateContainer(self.dbSelfLink, {"id": self.COLLECTIONAME})['_self']
        
        assert (self.collectionLink is not None)
        self.sprocReadAllExperimentLink = None
        sprocs = list(self.client.QueryStoredProcedures(self.collectionLink,
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters':[
                    { 'name':'@id', 'value':'returnAllExperimentList' }
                ]
            }))
        assert(sprocs), "Unable to get returnAllExperimentList sproc"
        self.sprocReadAllExperimentLink = sprocs[0]['_self']
        assert (self.sprocReadAllExperimentLink is not None)
        return
               
    def getClient(self):
        return self.client
    def getHost(self):
        return self.host
    def getDatabaseId(self):
        return self.databaseId    

    def setHost(value):
        self.Host = value
    def setKey(value):
        self.key = value
    def setDatabaseId(value):
        self.databaseId = value

    def logExperimentResult(self, documentDict, removeExisting=True):
        return self._insert_document_from_dict(documentDict, removeExisting)

    def returnAllCollection(self):
        self.preCheck()
        collections = list(self.client.ReadContainers(self.dbSelfLink))
        return collections, self.dbSelfLink

    def returnAllDocuments(self, collectionLink):
        self.preCheck()
        documentlist = list(self.client.ReadItems(collectionLink, {'maxItemCount':10}))
        return documentlist

    def returnDocument(self, documentLink):
        '''
        documentID contains the completeId
        '''
        self.preCheck()
        dObj = self.client.ReadItem(documentLink)
        return dObj

    def preCheck(self):
        assert(self.client is not None), "client set to Null!!!"
        assert(self.dbSelfLink is not None), "Database self link is set to Null!!!"
        assert(self.collectionLink is not None), "Collection self link is set to Null!!!"
        return

 
    ###########################################################################


    def saveLabelledImageListImpl(self, providerId, experimentName, dictObject):
        self._insert_document_in_collection(providerId, experimentName,dictObject)

    ###########################################################################


    def _insert_document_from_dict(self, dictObject, removeExisting=True):
        self.preCheck()
        assert(dictObject is not None), "dictObject parameter is mandatory!"

        providerId = dictObject[common._IMAGE_DETECTION_PROVIDER_TAG]
        experimentName = dictObject[common._EXPERIMENTNAME_TAG]

        assert(providerId is not None), "providerId parameter is mandatory in Dictionary!"
        assert(experimentName is not None), "experimentName parameter is mandatory in Dictionary!"
        

        return self._insert_document_in_collection(providerId, experimentName, dictObject, removeExisting)

    ###########################################################################

    def _insert_document_in_collection(self, providerId, experimentName, dictObject, removeExisting=True):
        '''
        checks for existence of a document, If it exists, deletes it and inserts
        a new record. checks for id as well as experiment name in the document. 
        providerId : Application compatible document Id, providerName
        '''
        self.preCheck()

        if removeExisting == True:
            self._removeExistingDocuments(providerId, experimentName)
                
        doc_id = self.client.CreateItem(self.collectionLink, dictObject)
        return doc_id

    ###########################################################################

    def _removeExistingDocuments(self,providerId, experimentName):
        docs = self._queryDocsForExistence(providerId, experimentName)
        # remove all the existing document first
        for doc in docs:
            self.client.DeleteItem(doc['_self'])

 
    ###########################################################################
    def returnLabelledImageListImpl(self, providerId, experimentName):
        return self._queryDocsForExistence(providerId, experimentName)

    ###########################################################################
    def _queryDocsForExistence(self, providerId, experimentName):
        '''
        '''
        self.preCheck()
        selectQuery = "SELECT * FROM r WHERE r." + self.IMAGE_DETECTION_PROVIDER +  "=@providerId and r." + self.EXPERIMENTNAME + "=@experimentID"
        documentquery = {
                "query": selectQuery ,
                "parameters": [ { "name":"@providerId", "value": providerId } ,
                                {"name":"@experimentID", "value": experimentName}]
                }
        results = None
        try:
            results = list(self.client.QueryItems(self.collectionLink, documentquery))
            return results
        except errors.HTTPFailure as e:
            if e.status_code == 404:
                print("Document doesn't exist")
                pass
            elif e.status_code == 400:
                # Can occur when we are trying to query on excluded paths
                print("Bad Request exception occured: ", e)
                pass
            else:
                print("Bad Request!")
                raise
        finally:
            print()
        return results

    def returnAllExperimentResultImpl(self):
        self.preCheck()
        # need to get the sproc_link 
        return self.client.ExecuteStoredProcedure(self.sprocReadAllExperimentLink, None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser = argparse.ArgumentParser(description=__doc__,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose", help="increase output verbosity",action="store_true")
    subparsers = parser.add_subparsers(dest="command")
    process_parser = subparsers.add_parser("logExperimentResult", help=cosmosWrapper.logExperimentResult.__doc__)

    process_parser.add_argument("host", nargs='?', default='')
    process_parser.add_argument("key", nargs='?',default='')
    process_parser.add_argument("databaseId", nargs='?', default='')
   
    args = parser.parse_args()

    if (args.verbose):
        TRACE_PRINT = True

    if args.command == "logExperimentResult":
        objRun = cosmosWrapper() #(args.host, args.key. args.databaseId)
        import datetime
        dictObject = {  'id': 'SomeFileName' + "_" + str(datetime.datetime.now()),  # this cannot be a numeric number!!!
                        'elapsedTime': "12:10:10",
                        'result-totalNumberOfRecords': 1234,
                        'result-true_true': 15,
                        'result-false_positive': 23,
                        'result-false_negative': 2,
                        'param-historyImage' : 10, 
                        'param-varThreshold' : 25, 
                        'param-numberOfIterations' : -1, 
                        'param-boundingRectAreaThreshold' : 1000, 
                        'param-contourCountThreshold' : 15,
                        'param-maskDiffThreshold' : 2,
                        'param-partOfFileName' : ''
                        }

        collectionName = "openCVImageExtractor"
        objRun.logExperimentResult(collectionName , dictObject, doChecks=True)
