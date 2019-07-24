#gunicorn -b 0.0.0.0:5555 -w 2 app:app
gunicorn --certfile=fullchain.pem --keyfile=privkey.pem -b 0.0.0.0:5555 -w 2 app:app
