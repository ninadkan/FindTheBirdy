# http
#curl -H "Content-Type: application/json" -H "Origin: http://localhost" -H "Access-Control-Request-Method: GET" --verbose http://0.0.0.0:5001/comsosDB/v1.0/collections
# https
curl -H "Content-Type: application/json" -H "Origin: https://localhost" -H "Access-Control-Request-Method: GET" --verbose https://ninadk-devserver.westeurope.cloudapp.azure.com:222/comsosDB/v1.0/collections

#curl -H "Content-Type: application/json" -H "Origin: http://localhost" -H "Access-Control-Request-Method: GET" --verbose http://localhost/comsosDB/v1.0/collections
#curl -H "Content-Type: application/json" -H "Origin: http://localhost" -H "Access-Control-Request-Method: GET" --verbose http://localhost:5001/comsosDB/v1.0/returnAllExperimentResult
#curl -H "Content-Type: application/json" -H "Origin: https://localhost" -H "Access-Control-Request-Method: POST" -d "{\"_sourceFileShareFolderName\":\"experiment-data\",\"_sourceDirectoryName\":\"object-detection\"}" --verbose https://localhost:443/azureStorage/v1.0/GetAllSourceUniqueExperimentNames
#curl -H "Content-Type: application/json" -H "Origin: https://localhost" -H "Access-Control-Request-Method: POST" -d "{\"_sourceFileShareFolderName\":\"experiment-data\",\"_sourceDirectoryName\":\"object-detection\"}" --verbose https://ninadk-devserver.westeurope.cloudapp.azure.com:443/azureStorage/v1.0/GetAllSourceUniqueExperimentNames