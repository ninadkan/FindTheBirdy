docker rm $(docker ps -aq)
docker image rm pythonmessagingapi:0.2
docker image rm computervisionproject.azurecr.io/pythonmessagingapi:0.2
docker build -f ./Dockerfile_PythonMessagingAPI -t pythonmessagingapi:0.2 ../Python
