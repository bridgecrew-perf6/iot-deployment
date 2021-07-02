const fs = require("fs");
const path = require("path");
const axios = require('axios');
const endpoint_url = "bauen40_tat.mts-server.de";
const config_login = {
    method: "post",
    url: `https://${endpoint_url}/UserPortalService.svc/json/Login`,
    headers: {
        "Content-Type": "application/json"
    }
};
(function () {
    creds = JSON.parse(
        fs.readFileSync(path.join(__dirname, "creds.json")).toString()
    )[endpoint_url];
    config_login.data = JSON.stringify({
        Username: creds.username,
        Password: creds.password
    });
})();
const config_get_assets = {
    method: "post",
    url: `https://${endpoint_url}/AssetPortalService.svc/json/GetAssets`,
    headers: {
        "Content-Type": "application/json"
    },
    data: JSON.stringify({})
};

module.exports = function (context, myTimer) {
    axios(config_login).then(function (response) {
        config_get_assets.headers["Cookie"] = response.headers["set-cookie"][0];
        axios(config_get_assets).then(function (response) {
            let resp_arr = response.data["Assets"];
            var date = new Date().toISOString();
            resp_arr.forEach(message => {
                message.deviceVendor = "mts_smart";
                message.deviceId = message.deviceVendor + "_" + message["AssetID"];
                message.enqueuedTimeUtc = date;
            });
            context.bindings.outputDocument = resp_arr;
            context.done();
        }).catch(function (err) {
            context.error(err);
            context.done();
        });
    }).catch(function (err) {
        context.error(err);
        context.done();
    });
};