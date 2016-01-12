function(doc) {
    if (doc.type == "node") {
        emit(doc._id, doc);
    }
    return;
};
