# this file  wraps CosmosDB API in python
# https://github.com/Azure/azure-cosmos-python
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

        self.LISTCONTAININGTRUEIMAGES = 'ListContainingTrueImages'
        self.LABELLEDIMAGES = 'LabelledImages'
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
        databases = list(self.client.QueryDatabases({
            "query": "SELECT * FROM r WHERE r.id=@id",
            "parameters": [
                { "name":"@id", "value": self.databaseId }
            ] }))
        if len(databases) > 0: # exists, take the first one
            self.dbSelfLink = databases[0]['_self'] 
        else:
            self.dbSelfLink = self.client.CreateDatabase({"id": self.databaseId})['_self']
        
        assert (self.dbSelfLink is not None)
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

    def logExperimentResult(self, collectionName , documentDict, doChecks=True):
        '''
        logs the informataion passed into cosmosDB
        '''
        
        assert(collectionName is not None), "collectionName parameter is mandatory!"
        assert(documentDict is not None), "documentDict parameter is mandatory!"
        assert(self.client is not None), "client set to Null!!!"
        assert(self.dbSelfLink is not None), "Database self link is set to Null!!!"
        
        
        coll= None
        if (doChecks == True):
            # find if any containers exist
            collections = list(self.client.QueryContainers( self.dbSelfLink,
                {"query": "SELECT * FROM r WHERE r.id=@id", "parameters": 
                [{ "name":"@id", "value": collectionName }]}))
            if len(collections) > 0:
                coll = collections[0] # take the first item
            else:
                coll = self.client.CreateContainer(self.dbSelfLink, {"id": collectionName})
        assert(coll is not None), "Unable to get collection object"

        doc_id = self.client.CreateItem(coll['_self'], documentDict)

        coll = None
        db = None

        # dObj = self.client.ReadItem(doc_id['_self'])
        # clean resources
        # self.client.DeleteItem(doc_id['_self'])
        # self.client.DeleteContainer(coll['_self'])
        # self.client.DeleteDatabase(db['_self'])
        return 

    


    def saveGoodPhotoListToCosmosDB(self, LabelledImagesPassed):
        assert(self.client is not None), "client set to Null!!!"
        assert(self.dbSelfLink is not None), "Database self link is set to Null!!!"
        
        #print("\n5. List all Collection in a Database")
        #print('Collections:')
        collections = list(self.client.ReadContainers(self.dbSelfLink))
        if not collections:
            return
        for collection in collections:
            #print(collection['id']) 
            dictObject = {'id': self.LISTCONTAININGTRUEIMAGES,
                          self.LABELLEDIMAGES : LabelledImagesPassed}
            doc_id = self.client.CreateItem(collection['_self'], dictObject)
            # dObj = self.client.ReadItem(doc_id['_self'])
            collection = None
        return


    # https://github.com/Azure/azure-cosmos-python/blob/master/samples/IndexManagement/Program.py#L152-L169
    def QueryDocumentsForTrueImages(self, collection_link):
        documentquery = {
                "query": "SELECT * FROM r WHERE r.id=@id",
                "parameters": [ { "name":"@id", "value": self.LISTCONTAININGTRUEIMAGES } ]
                }
        try:
            results = list(self.client.QueryItems(collection_link, documentquery))
            #print("Document(s) found by query: ")
            #for doc in results:
                #print(doc)
            return results
        except errors.HTTPFailure as e:
            if e.status_code == 404:
                print("Document doesn't exist")
            elif e.status_code == 400:
                # Can occur when we are trying to query on excluded paths
                print("Bad Request exception occured: ", e)
                pass
            else:
                raise
        finally:
            print()

    def QueryCollectionsWithQuery(self, experimentName):
        collectionquery = {
                "query": "SELECT * FROM r WHERE r.id=@id",
                "parameters": [ { "name":"@id", "value": experimentName } ]
                }
        try:
            results = list(self.client.QueryContainers(self.dbSelfLink, collectionquery))
            #print("Collection Found")
            #for collection in results:
                #print(collection)
            return results
        except errors.HTTPFailure as e:
            if e.status_code == 404:
                print("Collection doesn't exist")
            elif e.status_code == 400:
                # Can occur when we are trying to query on excluded paths
                print("Bad Request exception occured: ", e)
                pass
            else:
                raise
        finally:
            print()
        return 

    def savePhotoListToACollection(self, LabelledImagesPassed, experimentName ):
        collection = self.QueryCollectionsWithQuery(experimentName)
        for coll in collection: # there should be only one
            dictObject = {'id': self.LISTCONTAININGTRUEIMAGES,
                          self.LABELLEDIMAGES : LabelledImagesPassed}
            doc_id = self.client.CreateItem(coll['_self'], dictObject)
            coll = None
            return
        return 


    def returnGoodPhotoList(self, experimentName, doChecks=True):
        collection = self.QueryCollectionsWithQuery(experimentName)
        for coll in collection: # there should be only one
            docs = self.QueryDocumentsForTrueImages(coll['_self'])
            for document in docs : # there should be only one
                return document[self.LABELLEDIMAGES]

        return

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
