module.exports = function (context, IoTHubMessages) {
    if (!Array.isArray(IoTHubMessages) || IoTHubMessages.length <= 0) {
        return;
    }

    var [output_vemcon, output_mts_smart, output_exelonix] = [
        [],
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
                case "exelonix":
                    output_exelonix.push(message);
                default:
                    break;
            }
        }
    });

    context.bindings.outputDocumentVemcon = output_vemcon;
    context.bindings.outputDocumentMtsSmart = output_mts_smart;
    context.bindings.outputDocumentExelonix = output_exelonix;

    context.done();
};