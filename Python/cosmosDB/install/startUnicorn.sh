#gunicorn -b 0.0.0.0:5001 -w 2 cosmosDB-api:app
gunicorn --certfile=fullchain.pem --keyfile=privkey.key -b 0.0.0.0:443 -w 2 cosmosDB-api:app
