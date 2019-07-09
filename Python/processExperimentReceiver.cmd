REM #!/bin/bash
REM # second line needed to override the default consumergroup for starting the experiment
REM # export EVENT_HUB_RECEIVER_CONSUMER_GRP=startexperiment
REM # python eventProcessorHost.py
REM # type source startExperiment.sh
REM # for the environment variable to be set correctly
REM # python eventReceiver.py --partition 0 &
REM # python eventReceiver.py --partition 1 &
REM # python eventReceiver.py --partition 2 &
REM # python eventReceiver.py --partition 3
REM Two values of drain in Windows environment
set drain=
REM drain=-d True

start python eventReceiver.py -p 0 -c startexperiment %drain% &
start python eventReceiver.py -p 0 -c opencv %drain% &
start python eventReceiver.py -p 1 -c opencv %drain% &
start python eventReceiver.py -p 2 -c opencv %drain% &
start python eventReceiver.py -p 3 -c opencv %drain% &
start python eventReceiver.py -p 0 -c googledetector %drain% &
start python eventReceiver.py -p 0 -c azuredetector %drain% &
start python eventReceiver.py -p 0 -c yolodetector %drain% &
start python eventReceiver.py -p 0 -c mobilenet %drain% &
start python eventReceiver.py -p 0 -c tensorflow %drain%
