#!/bin/bash
# The above line is important, else you get some error
set -e
python --version
pip --version

#echo "INFO: starting SSH ..."
# not sure this is relevant for us, but anyway
service ssh start
# python azure-api.py
source ./startUnicorn.sh
