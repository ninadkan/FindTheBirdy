#!/bin/bash
# second line needed to override the default consumergroup for starting the experiment
# export EVENT_HUB_RECEIVER_CONSUMER_GRP=startexperiment
# python eventProcessorHost.py
# type source startExperiment.sh
# for the environment variable to be set correctly
# python eventReceiver.py --partition 0 &
# python eventReceiver.py --partition 1 &
# python eventReceiver.py --partition 2 &
# python eventReceiver.py --partition 3 
drain=False

sh -c 'python eventReceiver.py -p 0 -c startexperiment' &
sh -c 'python eventReceiver.py -p 0 -c opencv' &
sh -c 'python eventReceiver.py -p 1 -c opencv' &
sh -c 'python eventReceiver.py -p 2 -c opencv' &
sh -c 'python eventReceiver.py -p 3 -c opencv' &
sh -c 'python eventReceiver.py -p 0 -c googledetector' &
sh -c 'python eventReceiver.py -p 0 -c azuredetector -d '"$drain" &
sh -c 'python eventReceiver.py -p 0 -c yolodetector' &
sh -c 'python eventReceiver.py -p 0 -c mobilenet' &
sh -c 'python eventReceiver.py -p 0 -c tensorflow' 
