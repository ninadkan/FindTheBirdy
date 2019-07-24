#gunicorn -b 0.0.0.0:5002 -w 2 birdDetector-api:app
gunicorn --certfile=fullchain.pem --keyfile=privkey.pem -b 0.0.0.0:5002 -w 2 birdDetector-api:app
