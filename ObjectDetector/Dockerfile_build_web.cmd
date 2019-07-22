docker stop $(docker ps -aq) 
docker rm $(docker ps -aq)
docker rmi web:0.1
docker build -f ./Dockerfile_Web -t web:0.1 .
