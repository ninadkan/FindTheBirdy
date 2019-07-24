docker rm $(docker ps -aq)
docker image rm pythoncore:0.2
docker image rm computervisionproject.azurecr.io/pythoncore:0.2
docker build -f ./Dockerfile_PythonCore -t pythoncore:0.2 ../Python
