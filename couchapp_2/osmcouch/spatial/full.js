function(doc){
    if(doc.type == "node") {
	emit(doc.coords, null);
    }
}
