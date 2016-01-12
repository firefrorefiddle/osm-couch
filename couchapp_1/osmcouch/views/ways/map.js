function(doc) {
    if (doc.type == "way") {
        emit(doc._id, doc);
/*        
	if(doc.nodes) {
	    for(i=0;i<doc.nodes.length;++i) {
		emit([doc._id,1], {'_id': doc.nodes[i].toString()});
	    }
	}
*/
    }
    
    return;
};
