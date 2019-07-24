#!/bin/bash
#source keys.sh
#source processExperimentReceiver.sh
# wonderful way to get the environment variables passed. Brilliant. 
drain=${drain:=" "}

sh -c 'python eventReceiver.py -p 0 -c startexperiment ${drain}' &
sh -c 'python eventReceiver.py -p 0 -c opencv ${drain}' &
sh -c 'python eventReceiver.py -p 1 -c opencv ${drain}' &
sh -c 'python eventReceiver.py -p 2 -c opencv ${drain}' &
sh -c 'python eventReceiver.py -p 3 -c opencv ${drain}' &
sh -c 'python eventReceiver.py -p 0 -c googledetector ${drain}' &
sh -c 'python eventReceiver.py -p 0 -c azuredetector ${drain}' &
sh -c 'python eventReceiver.py -p 0 -c yolodetector ${drain}' &
sh -c 'python eventReceiver.py -p 0 -c mobilenet ${drain}' &
sh -c 'python eventReceiver.py -p 0 -c tensorflow ${drain}' 
