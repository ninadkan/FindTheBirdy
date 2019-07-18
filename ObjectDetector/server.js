/*
*  Copyright (c) Microsoft. All rights reserved. Licensed under the MIT license.
*  See LICENSE in the source repository root for complete license information.
*/

var express = require('express');
var app = express();
const https = require('https')
var morgan = require('morgan');
const fs = require('fs')
var path = require('path');

// Initialize variables.
var port = 6420; // process.env.PORT || 8080;


    // Configure morgan module to log all requests.
    app.use(morgan('dev'));

    // Set the front-end folder to serve public assets.
    app.use("/", express.static(__dirname));
    console.log(path.join(__dirname, '../../out'));
    app.use("/out", express.static(path.join(__dirname, "../../out")));
    app.use("/bower_components", express.static(path.join(__dirname, 'bower_components')));

    // Set up our one route to the index.html file.
    app.get('*', function (req, res) {
        res.sendFile(path.join(__dirname + '/index.html'));
    });


const httpsOptions = {
    key: fs.readFileSync('./security/cert.key'),
    cert: fs.readFileSync('./security/cert.pem')
}

//Start the server.
const server = https.createServer(httpsOptions, app)
    .listen(port, () => {
        console.log('server running at ' + port)
    })

// app.listen(port);
// console.log('Listening on port ' + port + '...'); 