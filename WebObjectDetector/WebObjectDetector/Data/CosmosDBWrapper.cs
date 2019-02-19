using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Threading.Tasks;
using Microsoft.Azure.Documents.Client;
using WebObjectDetector.Dashboard.Models;
namespace WebObjectDetector.Data
{
    public sealed class CosmosDBWrapper
    {

        string _databaseId = "";
        static Uri _endpointUri;
        static string _primaryKey = "";
        string _collectionId = "";
        Uri _databaseUri = null;
        Uri _documentCollectionUri = null; 


        public CosmosDBWrapper(Uri endpointUri, string primaryKey)
        {
            _databaseId = "experiment-find-the-birdy";
            _collectionId = "Operations"; 
            _endpointUri = endpointUri;
            _primaryKey = primaryKey;
        }

        private static DocumentClient _client = null;
        public static DocumentClient Instance {
            get
            {
                if (_client == null)
                {
                    _client = new DocumentClient(_endpointUri, _primaryKey);
                }
                return _client; 
            }
        }
        public async Task EnsureSetupAsync()
        {
            if (_databaseUri == null)
            {
                await Instance.CreateDatabaseIfNotExistsAsync(new Microsoft.Azure.Documents.Database { Id = _databaseId });
                _databaseUri = UriFactory.CreateDatabaseUri(_databaseId);
            }
            if (_documentCollectionUri == null)
            {
                await Instance.CreateDocumentCollectionIfNotExistsAsync(_databaseUri, new Microsoft.Azure.Documents.DocumentCollection() { Id = _collectionId });
                _documentCollectionUri = UriFactory.CreateDocumentCollectionUri(_databaseId, _collectionId);
            }
        }


        public async Task SaveOpencvOperationsAsync(OpencvOperations obj)
        {
            await EnsureSetupAsync();
            await Instance.UpsertDocumentAsync(_documentCollectionUri, obj);
        }

        public async Task<OpencvOperations> GetOpencvOperationsAsync(string Id)
        {
            await EnsureSetupAsync();
            var documentUri = UriFactory.CreateDocumentUri(_databaseId, _collectionId, Id);
            var result = await Instance.ReadDocumentAsync<OpencvOperations>(documentUri);
            return result.Document;
        }

        public async Task<HttpStatusCode> DeleteOpencvOperationsAsync(string Id)
        {
            await EnsureSetupAsync();
            var documentUri = UriFactory.CreateDocumentUri(_databaseId, _collectionId, Id);
            var result = await Instance.DeleteDocumentAsync(documentUri);
            return result.StatusCode;
        }

        public async Task<List<OpencvOperations>> GetOpencvOperationsAsync()
        {
            await EnsureSetupAsync();
            // build the query
            var feedOptions = new FeedOptions() { MaxItemCount = -1 };
            var query = Instance.CreateDocumentQuery<OpencvOperations>(_documentCollectionUri, "Select * from c", feedOptions);

            var results = new List<OpencvOperations>();
            foreach (OpencvOperations item in query)
            {
                results.Add(item); 
            }
            return results;
        }
    }
}
