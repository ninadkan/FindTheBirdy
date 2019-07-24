docker rm $(docker ps -aq)
docker image rm pythonapi:0.2
docker image rm computervisionproject.azurecr.io/pythonapi:0.2
docker build -f ./Dockerfile_PythonAPI -t pythonapi:0.2 ../Python
