module.exports = async function (context, documents) {
    if (!Array.isArray(documents) || documents.length <= 0) {
        return;
    }

    documents.forEach(document => {
        document.id = document.deviceId;
    });

    context.bindings.outputDocument = documents;
}