docker rm $(docker ps -aq)
docker rmi pythonmessagingapi:0.2
docker build -f ./Dockerfile_PythonMessagingAPI -t pythonmessagingapi:0.2 .
