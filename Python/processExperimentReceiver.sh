#!/bin/bash
# second line needed to override the default consumergroup for starting the experiment
# export EVENT_HUB_RECEIVER_CONSUMER_GRP=startexperiment
# python eventProcessorHost.py
# type source startExperiment.sh
# for the environment variable to be set correctly
python eventReceiver.py --partition 0 &
python eventReceiver.py --partition 1 &
python eventReceiver.py --partition 2 &
python eventReceiver.py --partition 3 