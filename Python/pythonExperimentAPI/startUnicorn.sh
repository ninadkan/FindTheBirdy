gunicorn -b 0.0.0.0:5002 -w 2 birdDetector-api:app
#gunicorn --certfile=fullchain.pem --keyfile=privkey.key -b 0.0.0.0:443 -w 2 birdDetector-api:app
