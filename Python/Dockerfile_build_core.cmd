docker rm $(docker ps -aq)
docker rmi pythoncore:0.2
docker build -f ./Dockerfile_PythonCore -t pythoncore:0.2 .
