function(doc, req) {
    if(req.fresh_import == "true") {
	new_doc = req;
	new_doc._rev = doc._rev;
	return [new_doc, 'ok'];
    } else {
	return [doc, 'ok'];
    }
}
