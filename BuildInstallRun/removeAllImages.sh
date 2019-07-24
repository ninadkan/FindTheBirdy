#!/bin/bash
sudo docker stop $(sudo docker ps -aq)
sudo docker rm $(sudo docker ps -aq)
sudo docker rmi web:0.2
sudo docker rmi pythoncore:0.2
sudo docker rmi pythonapi:0.2
sudo docker rmi pythonmessagingapi:0.2
sudo docker images