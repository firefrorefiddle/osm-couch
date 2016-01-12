/*function(_dummy, values, _rereduce) {
    
    have_waydoc=false;
    retval=[]

    for(i=0; i<values.length; i++) {
	if(values[i].type == "way") {
	    have_waydoc = true;
	    tmp = values[i];
	    tmp.full_nodes = retval;
	    retval = tmp;
	} else {
	    if(values[i].type == "full_node_list") {
		if(have_waydoc) {
		    retval.full_nodes.concat(values[i].full_nodes);
		} else
		{
		    retval.concat(values[i].full_nodes);
		}
	    } else {
		// values[i].type is node
		if(have_waydoc) {
		    retval.full_nodes.push(values[i].coords);
		} else {
		    retval.push(values[i].coords);
		}
	    }
	}
    }

    if(retval.type == "way") {
	return retval;
    } else {   
	return {"type": "full_node_list", "full_nodes": retval};
    }
}
*/
