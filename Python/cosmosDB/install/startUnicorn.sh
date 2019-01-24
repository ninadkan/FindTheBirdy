#gunicorn -b 0.0.0.0:5001 -w 2 cosmosDB-api:app
gunicorn --certfile=xip.io.crt --keyfile=xip.io.key -b 0.0.0.0:443 -w 2 cosmosDB-api:app
