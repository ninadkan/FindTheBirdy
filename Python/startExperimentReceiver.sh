#!/bin/bash
# second line needed to override the default consumergroup for starting the experiment
export EVENT_HUB_RECEIVER_CONSUMER_GRP=startexperiment
# python eventProcessorHost.py
python eventReceiver.py -p 0