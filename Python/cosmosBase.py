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


# pip install azure-cosmos, sort of works!!! 


import azure.cosmos.cosmos_client as document_client
import azure.cosmos.errors as errors
import argparse

# import sys
# sys.path.insert(0, '../') # needed as common is in the parent folder
import common



def ifNullReadAndAssignFromEnviron(variableName, KEY):
    import os
    if (variableName is None) or (len(variableName) == 0 ):
        variableName = os.environ.get(KEY)
    return variableName

###############################################################################   

class cosmosBase:
    def __init__(self, host, key, databaseId, collectionName):
        # self.ID_FOR_USER_DETECTION = common._ID_FOR_USER_DETECTION
        # self.DETECTED_IMAGES_TAG = common._DETECTED_IMAGES_TAG
        # self.EXPERIMENTNAME = common._EXPERIMENTNAME_TAG
        # self.IMAGE_DETECTION_PROVIDER = common._IMAGE_DETECTION_PROVIDER_TAG
        
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

        self.collectionLink = self.getCollection(collectionName)
        assert (self.collectionLink is not None), "Unable to get collection: " + collectionName
        self.preCheckBase()
        return 

    def getCollection(self, collectionName):
        """
        returns the collection link and if the collection does not exists, it creates it
        """
        # find if any containers exist
        collectionLink = None
        collections = list(self.client.QueryContainers( self.dbSelfLink,
            {"query": "SELECT * FROM r WHERE r.id=@id", "parameters": 
            [{ "name":"@id", "value": collectionName }]}))
        if len(collections) > 0:
            collectionLink = collections[0]['_self'] # take the first item
        else:
            collectionLink = self.client.CreateContainer(self.dbSelfLink, {"id": collectionName})['_self']
        
        return collectionLink


    def getClient(self):
        return self.client
    def getHost(self):
        return self.host
    def getDatabaseId(self):
        return self.databaseId    
    def getDatabaseSelfLink(self):
        return self.dbSelfLink
    def getCollectionSelfLink(self):
        return self.collectionLink

    # def setHost(self, value):
    #     self.Host = value
    # def setKey(self, value):
    #     self.key = value
    # def setDatabaseId(self, value):
    #     self.databaseId = value
    # def setDatabaseSelfLink(self, value):
    #     self.dbSelfLink = value
    # def setCollectionSelfLink(self,value):
    #     self.collectionLink = value

    def returnAllCollection(self):
        self.preCheckBase()
        collections = list(self.client.ReadContainers(self.dbSelfLink))
        return collections, self.dbSelfLink

    def preCheckBase(self):
        assert(self.client is not None), "client set to Null!!!"
        assert(self.dbSelfLink is not None), "Database self link is set to Null!!!"
        assert(self.collectionLink is not None), "Collection self link is set to Null!!!"
        return

    def removeExistingDocuments(self, docs):
        for doc in docs:
            self.client.DeleteItem(doc['_self'])

    def returnAllDocuments(self, collectionLink):
        return list(self.client.ReadItems(collectionLink, {'maxItemCount':10}))

    def returnDocument(self, documentLink):
        return self.client.ReadItem(documentLink)

    def createItem(self, dictObject):
        return self.client.CreateItem(self.collectionLink, dictObject)

    def getDocumentFromQuery(self, query):
        results = None
        try:
            results = list(self.client.QueryItems(self.collectionLink, query))
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

    def getStoredProcLink(self, storedProcName):
        sprocLink = None
        sprocs = list(self.client.QueryStoredProcedures(self.collectionLink,
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters':[
                    { 'name':'@id', 'value':storedProcName }
                ]
            }))
        assert(sprocs), "Unable to get sproc {}".format(storedProcName)
        if (sprocs is not None and len(sprocs)> 0):
            sprocLink = sprocs[0]['_self']
        return sprocLink
    
    # def test(self):
    #     sproc3 = {
    #         'id': 'storedProcedure3',
    #         'body': (
    #             'function (input) {' +
    #                 '  getContext().getResponse().setBody(' +
    #                 '      \'a\' + input.temp);' +
    #             '}')
    #     }
        
    #     #retrieved_sproc3 = self.client.CreateStoredProcedure(self.collectionLink,sproc3)
    #     spLink = self.getStoredProcLink('storedProcedure3')
    #     result = self.client.ExecuteStoredProcedure(spLink,
    #                                             {'temp': 'so'})
    #     print(result)
        

###############################################################################

class clsCosmosOperationsBase(cosmosBase):
    def __init__(self, mandatoryColumns, collectionName, host='', key='', databaseId=''):
        super().__init__(host, key, databaseId, collectionName) # common._OPERATIONSCOLLECTIONNAME)
        self.mandatoryColumnList = mandatoryColumns
        return
    # -------------------------------------------------------------------------

    def insert_document_from_dict(self, dictObject, removeExisting=True):
        assert(dictObject is not None), "dictObject parameter is mandatory!"
        assert(self.mandatoryColumnList is not None and len(self.mandatoryColumnList) > 0), "MandatoryColumnList error"
        # check that each mandatiry parameter has been specified
        for item in self.mandatoryColumnList:
            assert(dictObject[item] is not None), "Passed dictionary object does not contain item =" + item
        return self._insert_document_in_collection(dictObject, removeExisting)
    # -------------------------------------------------------------------------

    def insert_document_in_collection(self, dictObject, removeExisting=True):
        '''
        checks for existence of a document, If it exists, deletes it and inserts
        a new record. checks for id as well as experiment name in the document. 
        providerId : Application compatible document Id, providerName
        '''
        if removeExisting == True:
            self.removeExistingDocumentDict(dictObject)
        return super().createItem(dictObject)
    # -------------------------------------------------------------------------

    def removeExistingDocumentDict(self, dictObject, bNocheck = False):
        #'if bNoCheck is set to True, it bypasses all checks and deletes all the records 
        #which matched the dictionary object'
        if (bNocheck == True):
            lst = self._queryDocsForExistence(dictObject)
        else:
            lst = self.queryDocsForExistenceWithCheck(dictObject) 
        if (lst is not None):
            super().removeExistingDocuments(lst)
        return
    # -------------------------------------------------------------------------

    def getValue(self, dictObject, key):
        value = None
        doc = self.getDocument(dictObject)
        if (doc is not None):
            value = doc[key]
        return value

    # -------------------------------------------------------------------------      

    def getDocuments(self, dictObject, bNoCheck = False):
        if (bNoCheck == True):
            return( self._queryDocsForExistence(dictObject))
        else:
            return (self.queryDocsForExistenceWithCheck(dictObject))
    # ------------------------------------------------------------------------- 

    def getDocument(self, dictObject):
        firstItem = None
        docs = self.queryDocsForExistenceWithCheck(dictObject)
        if (docs is not None and len(docs) > 0):
            firstItem = docs[0]
        return firstItem        

    # -------------------------------------------------------------------------
    
    def queryDocsForExistenceWithCheck(self, dictObject):
        assert(self.mandatoryColumnList is not None and len(self.mandatoryColumnList) > 0), "No mandatoryColumnList specified"
        numberOfParameters = len(self.mandatoryColumnList)
        paramName = "@param"
        selectQuery = 'SELECT * FROM r WHERE r.'
        count = 0
        parameters = []

        for item in self.mandatoryColumnList:
            parameterName = paramName + str(count)
            selectQuery += item + '=' + parameterName
            
            count += 1
            if (count < (numberOfParameters)):
                selectQuery += ' and r.'
            assert(dictObject[item] is not None), "Error, mandatory item not specified" + item
            parameters.append({"name":parameterName, "value": dictObject[item]})

        #print(selectQuery)
        #print(parameters)

        documentquery = { "query": selectQuery , "parameters": parameters }
        return super().getDocumentFromQuery(documentquery)
    # -------------------------------------------------------------------------

    def _queryDocsForExistence(self, kwargs):
        if kwargs is not None:
            numberOfParameters = len(kwargs)
            paramName = "@param"
            selectQuery = 'SELECT * FROM r WHERE r.'
            count = 0
            parameters = []

            for key in kwargs:
                parameterName = paramName + str(count)
                selectQuery += key + '=' + parameterName
                
                count += 1
                if (count < (numberOfParameters)):
                    selectQuery += ' and r.'
                parameters.append({"name":parameterName, "value": kwargs[key]})

            #print(selectQuery)
            #print(parameters)
            documentquery = { "query": selectQuery , "parameters": parameters }
            return super().getDocumentFromQuery(documentquery)
        else:
            return None
