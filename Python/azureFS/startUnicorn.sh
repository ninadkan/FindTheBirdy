#gunicorn -b 0.0.0.0:5000 -w 4 azure-api:app
gunicorn --certfile=xip.io.crt --keyfile=xip.io.key -b localhost:443 -w 4 azure-api:app
