#http
#curl -H "Origin: http://localhost" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: X-Requested-With" -X OPTIONS --verbose http://localhost:5000/azureStorage/v1.0/GetAllSourceUniqueExperimentNames
#https
curl -i -k -H "Origin: https://localhost" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: X-Requested-With" -X OPTIONS --verbose https://ninadk-devserver.westeurope.cloudapp.azure.com:443/azureStorage/v1.0/GetAllSourceUniqueExperimentNames
