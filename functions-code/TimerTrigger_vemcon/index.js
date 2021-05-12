const fs = require('fs');
const path = require('path');
const https = require('https');
const endpoint_1 = 'api.vemcon.net';
const options = {
    hostname: endpoint_1,
    port: 443,
    path: '/tt/v0/tooltrackers',
    method: 'GET',
    headers: {
        'x-api-key': JSON.parse(
            fs.readFileSync(path.join(__dirname, 'creds.json'))
        )[endpoint_1]['x-api-key']
    }
};
module.exports = function (context, myTimer) {
    let output = '';

    const req = https.request(options, (res) => {
        res.setEncoding('utf8');

        res.on('data', (chunk) => {
            output += chunk;
        });

        res.on('end', () => {
            var date = new Date().toISOString();
            resp_arr = JSON.parse(output.replace(/\bNaN\b/g, 'null'));
            resp_arr.forEach(message => {
                message.deviceVendor = 'vemcon';
                message.deviceId = message.deviceVendor + '_' + message['tooltracker']['ttid'];
                message.enqueuedTimeUtc = date;
                delete message['motion']['history'];
            });
            context.bindings.outputDocument = resp_arr;
            context.done();
        });
    });
    req.on('error', (err) => {
        context.error(err);
        context.done();
    });

    req.end();
};