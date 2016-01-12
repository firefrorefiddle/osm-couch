
function(head, req) {
    // implement JSON.stringify serialization
    JSON.stringify = JSON.stringify || function (obj) {
	var t = typeof (obj);
	if (t != "object" || obj === null) {
            // simple data type
            if (t == "string") obj = '"'+obj+'"';
            return String(obj);
	}
	else {
            // recurse array or object
            var n, v, json = [], arr = (obj && obj.constructor == Array);
            for (n in obj) {
		v = obj[n]; t = typeof(v);
		if (t == "string") v = '"'+v+'"';
		else if (t == "object" && v !== null) v = JSON.stringify(v);
		json.push((arr ? "" : '"' + n + '":') + String(v));
            }
            return (arr ? "[" : "{") + String(json) + (arr ? "]" : "}");
	}
    };

    provides("text", function() {

	var out = {'value': {'nodes': []}};

	send("{\"total_rows\":\""+head.total_rows+"\", \"rows\": [");

	while(row=getRow()) {
	   
	    if(row.key[1] == 0)
	    {
		if(out.value.length>0)
		{
		    send(JSON.stringify(out.value));
		} 
		out=row;
	    } else {

		var missing=0;

		for(var i=0; i<out.value.nodes.length; ++i)
		{

		    if(out.value.nodes[i] == row.value._id)
		    {
			out.value.nodes[i] = row.value.coords;
		    }

		    if(parseInt(out.value.nodes[i]) == out.value.nodes[i])
			++missing;
		    
		} 		

		if(missing == 0)
		{
		    send(JSON.stringify(out.value));
		    out = {'value': {'nodes': []}};
		}
	    }
	}

	if(out.value.length > 0)
	{
	    send(JSON.stringify(out.value));
	}

	send("]}");
    }); 
}

