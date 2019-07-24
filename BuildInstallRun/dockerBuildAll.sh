#!/bin/bash
# Assumes that all the images have been removed
sudo docker build -f ./Dockerfile_PythonAPI -t pythonapi:0.2 ../Python
sudo docker build -f ./Dockerfile_PythonCore -t pythoncore:0.2 ../Python
sudo docker build -f ./Dockerfile_PythonMessagingAPI -t pythonmessagingapi:0.2 ../Python
sudo docker build -f ./Dockerfile_Web -t web:0.2 ../ObjectDetector