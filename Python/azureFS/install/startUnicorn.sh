#gunicorn -b 0.0.0.0:5000 -w 4 azure-api:app
gunicorn --certfile=fullchain.pem --keyfile=privkey.key -b 0.0.0.0:443 -w 2 azure-api:app
