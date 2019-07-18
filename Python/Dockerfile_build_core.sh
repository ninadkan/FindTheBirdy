# uncomment the docker image that you don't want to build
#sudo docker build -f ./Dockerfile -t opencv:0.1 .
sudo docker build -f ./Dockerfile_AzureFS -t azurefs:0.1 .
sudo docker build -f ./Dockerfile_CosmosDB -t cosmosdb:0.1 .