#!/bin/bash
# The above line is important, else you get some error
set -e

python --version
pip --version

#echo "INFO: starting SSH ..."
# not sure this is relevant for us, but anyway
service ssh start

source ./startUnicorn.sh
#gunicorn -b 0.0.0.0:5001 -w 2 cosmosDB-api:app
#gunicorn --certfile=xip.io.crt --keyfile=xip.io.key -b 0.0.0.0:443 -w 2 cosmosDB-api:app

