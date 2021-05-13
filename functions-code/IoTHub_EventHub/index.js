module.exports = function (context, IoTHubMessages) {
    if (!Array.isArray(IoTHubMessages) || IoTHubMessages.length <= 0) {
        return;
    }

    var [output_vemcon, output_mts_smart] = [
        [],
        []
    ];
    IoTHubMessages.forEach((message, i) => {
        if ("deviceVendor" in message) {
            message.deviceId = context.bindingData.systemPropertiesArray[i]["iothub-connection-device-id"];
            message.enqueuedTimeUtc = context.bindingData.enqueuedTimeUtcArray[i];
            switch (message["deviceVendor"]) {
                case "vemcon":
                    output_vemcon.push(message);
                    break;
                case "mts_smart":
                    output_mts_smart.push(message);
                    break;
                default:
                    break;
            }
        }
    });

    context.bindings.outputDocument_vemcon = output_vemcon;
    context.bindings.outputDocument_mts_smart = output_mts_smart;

    context.done();
};