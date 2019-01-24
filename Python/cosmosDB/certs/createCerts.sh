echo 'starting generating certificates and keys...'
openssl genrsa -out xip.io.key 1024
echo '...key done . csr ...'
openssl req -new -key xip.io.key -out xip.io.csr
echo '...csr done . crt ...'
openssl x509 -req -days 365 -in xip.io.csr -signkey xip.io.key -out xip.io.crt
echo '...crt done . concatenating for pem ...'
cat xip.io.crt xip.io.key | tee xip.io.pem
echo "...all Done"