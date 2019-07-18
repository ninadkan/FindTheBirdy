REM uncomment the docker image that you don't want to build
REM sudo docker build -f ./Dockerfile -t opencv:0.1 .
REM docker build -f ./Dockerfile_AzureFS -t azurefs:0.1 .
REM docker build -f ./Dockerfile_CosmosDB -t cosmosdb:0.1 .
docker rm $(docker ps -aq)
docker rmi pythonapi:0.1
docker build -f ./Dockerfile_PythonAPI -t pythonapi:0.1 .
REM docker run -e drain=' -d True ' pythoncore:0.1
REM docker run pythoncore:0.1
REM docker run --entrypoint=/bin/bash -it pythoncore:0.1