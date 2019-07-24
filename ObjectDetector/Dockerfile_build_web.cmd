docker stop $(docker ps -aq) 
docker rm $(docker ps -aq)
docker rmi web:0.2
docker build -f ../../ObjectDetector/Dockerfile_Web -t web:0.2 .
