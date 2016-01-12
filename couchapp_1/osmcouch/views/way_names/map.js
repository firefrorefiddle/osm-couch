function(doc) {
    if (doc.type == "way" && doc.tags && doc.tags["name"]) {
        emit(doc.tags["name"], null);
    }
    return;
};
