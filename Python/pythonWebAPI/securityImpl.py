from validateJWT import InvalidAuthorizationToken, validateJWT
#from flask import Flask, jsonify, abort, make_response
from flask import request, Response
from expiringdict import ExpiringDict
import json
import storageBlobService

import appSecrets
import cosmosDBApiMapper

import sys
sys.path.insert(0, '../') # needed as common is in the parent folder
import storageFileService
from cosmosDBWrapper import clsCosmosWrapper
from cosmosImageOperations import clsCosmosImageProcessingOperations
from cosmosStatusUpdate import clsStatusUpdate


import json
import logging

import sys
sys.path.insert(0, '../')
import common
from loggingBase import clsLoggingBase

MX_NUM_USER=1000
MX_TOKEN_AGE=300 # seconds, 5 minutes

class securityImpl(clsLoggingBase):
    """
    This class acts as the controller of everything related to security.
    Single instance of this class should be created 
    """
    def __init__(self):
        super().__init__(__name__)
        self.jwtValidator = validateJWT()
        self.valid_audiences = [appSecrets.ClientId, appSecrets.serviceIdentifierUri]
		#self.ClientId = appSecrets.ClientId
		#self.ClientSecret = appSecrets.ClientSecret
		#self.TenantId = appSecrets.TenantId
        self.userIdCache = ExpiringDict(max_len=MX_NUM_USER, max_age_seconds=MX_TOKEN_AGE)
        self.storageObject = storageBlobService.StorageBlobServiceWrapper(appSecrets.KV_Storage_AccountName)
        self.storageFileObject = storageFileService.storageFileService(appSecrets.KV_Storage_AccountName)

        self.storageKeyLoaded = False
        self.clsObj = None           # our global instance
        self.clsImageOperations = None    # our global instance
        self.clsStatusOperations = None
        self.cosmosDBObjCreated = False
        
        return

    def get_StorageObject(self):
        return self.storageObject

    def get_fileStorageObject(self):
        return self.storageFileObject

    def get_clsObject(self):
        return self.clsObj

    def get_clsImageOperations(self):
        return self.clsImageOperations

    def get_clsStatusOperations(self):
        return self.clsStatusOperations

    def validateRequest(self,request):
        super().getLoggingObj().debug("validateRequest")
        bRV = False
        response = None
        scopeTest = 'user_impersonation'

        # first ask the jwt to validate that the request contains correct Bearer token
        btempRV, bearerToken, decodedToken = self.jwtValidator.validate_request(request)
        if (btempRV and bearerToken and decodedToken):
            # further validation 
            if (decodedToken['aud'] in self.valid_audiences):       # audience should include our instance
                if (decodedToken['scp'] == scopeTest):             # for the user_impersonation, this value should be present
                    # assume ['oid'] value is present in our cache 
                    if (decodedToken['oid'] not in self.userIdCache):
                        # indicates that we've not seen this user before. 
                        # Validate that he/she has
                        # been authorised to access the KeyVault APIs
                        btempRV, response = self.validateUserCredentials(bearerToken)
                        if (btempRV):
                            # add into our cache
                            self.userIdCache['oid'] = bearerToken
                            # If our Storage API Keys are not loaded, now is the time to load them
                            # Remember, this is executed only once for the first authenticated/authorised user
                            if (self.storageKeyLoaded == False):
                                access_token = json.loads(response.text)
                                # Assume that our storage access was not created and create it
                                storage_key_list, response = self.getStorageKeySecret(access_token)
                                # Also creates the storage service internally
                                if (storage_key_list):
                                    if (len(storage_key_list) > 0 ):
                                        #print(storage_key_list[0])
                                        self.storageObject.set_storageKey(storage_key_list[0])
                                        self.storageFileObject.set_storageKey(storage_key_list[0])
                                        self.storageKeyLoaded = True
                                        bRV = True # set this to true now. 
                                    if (self.cosmosDBObjCreated == False):
                                        print("creating cosmos secure object")
                                        if (len(storage_key_list) >= 4 ):
                                            #print(storage_key_list[1])
                                            #print(storage_key_list[2])
                                            #print(storage_key_list[3])      
                                            self.clsObj = clsCosmosWrapper(host=storage_key_list[1], key = storage_key_list[2], databaseId=storage_key_list[3])
                                            self.clsImageOperations = clsCosmosImageProcessingOperations(host=storage_key_list[1], key = storage_key_list[2], databaseId=storage_key_list[3])
                                            self.clsStatusOperations = clsStatusUpdate(host=storage_key_list[1], key = storage_key_list[2], databaseId=storage_key_list[3])
                                            self.cosmosDBObjCreated = True
                                            bRV = True
                            else:
                                bRV = True
                else:
                    response = Response('Unauthorized', 401, {'Content-Type': 'text/html', 'WWW-Authenticate': 'Invalid Scope'})
            else:
                response = Response('Unauthorized', 401, {'Content-Type': 'text/html', 'WWW-Authenticate': 'Invalid Audience'})
        else:
            response = Response('Unauthorized', 401, {'Content-Type': 'text/html', 'WWW-Authenticate': 'Bearer Token, Decoded Token security error'})
        return bRV, response
       
    def validateUserCredentials(self,bearerToken) :
        super().getLoggingObj().debug("validateUserCredentials")
        bRV = False
        r = None
        try:
            r = self.get_token_with_authorization_code(bearerToken)
            if (r.status_code >= 200 and r.status_code < 300):
                bRV = True
        except Exception as ex:
            r = Response('Unauthorized', 401, {'Content-Type': 'text/html', 'WWW-Authenticate': ex})
        except models.KeyVaultErrorException as kex:
            r = Response('Unauthorized', 401, {'Content-Type': 'text/html', 'WWW-Authenticate': kex})
        return bRV, r
   
    def get_token_with_authorization_code(self, bearerToken):
        super().getLoggingObj().debug("get_token_with_authorization_code")
        import requests

        resp = None

        # construct our Azure AD obo message
        grant_type= 'urn:ietf:params:oauth:grant-type:jwt-bearer'
        resourceKeyVault ="https://vault.azure.net"
        requested_token_use= 'on_behalf_of'
        scope='openid'

        headers = {'content-type': 'application/x-www-form-urlencoded'}
        # Working example
        params = {
            'grant_type': grant_type,
            'client_id': appSecrets.ClientId,
            'client_secret' : appSecrets.ClientSecret,
            'resource': resourceKeyVault,
            'requested_token_use': requested_token_use,
            'scope': scope,
            'assertion': bearerToken
        }

        URL = 'https://login.microsoftonline.com/{0}/oauth2/token'.format(appSecrets.TenantId)
        resp = requests.post(URL, headers=headers,  data=params) 
        return resp

    def getStorageKeySecret(self,token_credentials):
        super().getLoggingObj().debug("getStorageKeySecret")
        from msrestazure.azure_active_directory import AADTokenCredentials
        resourceKeyVault ="https://vault.azure.net"
        secret_bundle = []
        try:
            credentials = AADTokenCredentials(
                token = token_credentials,
                client_id = appSecrets.ClientId,
                tenant = appSecrets.TenantId,
                resource = resourceKeyVault
            )
   
            from azure.keyvault import KeyVaultClient, KeyVaultAuthentication
            from azure.keyvault.models import KeyVaultErrorException
    
            #Works the following
            kvAuth = KeyVaultAuthentication(credentials=credentials)
            client = KeyVaultClient(kvAuth)

            # Following will also work, if the WebAPI is given permission to access Key Vault permissions
            #client = KeyVaultClient(KeyVaultAuthentication(auth_callback))
        
            rv = client.get_secret( appSecrets.KV_VAULT_URL, 
                                    appSecrets.KV_Storage_AccountKeyName, 
                                    appSecrets.KV_Storage_SECRET_VERSION)
            print(rv)
            secret_bundle.append(rv.value)
            # first the HOST Value
            secret_bundle.append(client.get_secret(appSecrets.KV_VAULT_URL, 
                                                    appSecrets.KV_COSMOSDB_HOST, 
                                                    appSecrets.KV_Storage_SECRET_VERSION).value)
            # Next the Key value
            secret_bundle.append(client.get_secret(appSecrets.KV_VAULT_URL, 
                                                    appSecrets.KV_COSMOSDB_KEY, 
                                                    appSecrets.KV_Storage_SECRET_VERSION).value)
            # and finally the database value
            secret_bundle.append(client.get_secret(appSecrets.KV_VAULT_URL, 
                                                    appSecrets.KV_COSMOSDB_DATABASE, 
                                                    appSecrets.KV_Storage_SECRET_VERSION).value)                                                                                

        except KeyVaultErrorException as ex:
            print(ex)
            rnce = ex.response
            return None, rnce
        except Exception as eex:
            print(eex)
            return None, None
        return secret_bundle, None

    def auth_callback(server, resource, scope):
        '''
        This function is not called /should not be called in normal circumstances; Only relevant for 
        testing to see that the Azure Vault access is provided directly by the Web API application as well.
        '''
        from azure.common.credentials import ServicePrincipalCredentials

        credentials = ServicePrincipalCredentials(
            client_id = appSecrets.ClientId,
            secret = appSecrets.ClientSecret,
            tenant = appSecrets.TenantId,
            resource = resource
        )
        token = credentials.token

        #if __debug__:
        #    import webbrowser
        #    url = 'https://jwt.ms/#access_token=' + token['access_token']
        #    webbrowser.open(url, new=0, autoraise=True)    
        return token['token_type'], token['access_token']


