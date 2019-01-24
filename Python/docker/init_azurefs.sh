#!/bin/bash
# The above line is important, else you get some error
set -e

python --version
pip --version

#echo "INFO: starting SSH ..."
service ssh start
# python azure-api.py
# gunicorn -b localhost:443 -w 4 azure-api:app
gunicorn --certfile=xip.io.crt --keyfile=xip.io.key -b localhost:443 -w 4 azure-api:app