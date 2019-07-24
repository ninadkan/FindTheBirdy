docker stop $(docker ps -aq) 
docker image rm web:0.2
docker image rm computervisionproject.azurecr.io/web:0.2
docker build -f ./Dockerfile_Web -t web:0.2 ../ObjectDetector
