docker rm $(docker ps -aq)
docker rmi pythonapi:0.2
docker build -f ./Dockerfile_PythonAPI -t pythonapi:0.2 .
