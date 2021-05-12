module.exports = function (context, IoTHubMessages) {
    if (!Array.isArray(IoTHubMessages) || IoTHubMessages.length <= 0) {
        return;
    }

    var i = IoTHubMessages.length - 1;
    while (i >= 0) {
        if (!("deviceVendor" in IoTHubMessages[i])) {
            IoTHubMessages.splice(i, 1);
        } else {
            IoTHubMessages[i].deviceId = context.bindingData.systemPropertiesArray[i]["iothub-connection-device-id"];
            IoTHubMessages[i].enqueuedTimeUtc = context.bindingData.enqueuedTimeUtcArray[i];
        }
        i -= 1;
    }
    context.bindings.outputDocument = IoTHubMessages;

    context.done();
};