const fs = require("fs");
const path = require("path");
const axios = require('axios');
const endpoint_url = "api.vemcon.net";
const config = {
    url: `https://${endpoint_url}/tt/v0/tooltrackers`,
    method: "get",
    headers: {
        "x-api-key": JSON.parse(
            fs.readFileSync(path.join(__dirname, "creds.json")).toString()
        )[endpoint_url]["x-api-key"]
    }
};
module.exports = function (context, myTimer) {
    axios(config).then(function (response) {
        let resp_arr = response.data;
        var date = new Date().toISOString();
        resp_arr.forEach(message => {
            message.deviceVendor = "vemcon";
            message.deviceId = message.deviceVendor + "_" + message["tooltracker"]["ttid"];
            message.enqueuedTimeUtc = date;
            delete message["motion"]["history"];
        });
        context.bindings.outputDocument = resp_arr;
        context.done();
    }).catch(function (err) {
        context.error(err);
        context.done();
    });
};