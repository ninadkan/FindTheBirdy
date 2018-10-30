# Following file is 273 MB and its downloaded as the certificate installed is local one 
# certificate comment is applicable to every  other doenload as well 
wget --no-check-certificate https://pjreddie.com/media/files/yolov3.weights -O ./yolov3.weights
wget --no-check-certificate https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg?raw=true -O ./yolov3.cfg
wget --no-check-certificate https://github.com/pjreddie/darknet/blob/master/data/coco.names?raw=true -O ./coco.names

# For Linux systems
wget https://pjreddie.com/media/files/yolov3.weights -O ./yolov3.weights