function(doc) {
    if (doc.type == "way") {
        emit([doc._id,0], doc);
    } else if (doc.type == "node") {
	for(i=0;i<doc.ways.length;++i) {
            emit([doc.ways[i],1], doc);
	    }
    }
};
