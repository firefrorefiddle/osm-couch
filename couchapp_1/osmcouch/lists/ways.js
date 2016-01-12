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

function(head, req) {
    provides("text", function() {

	var out = {};

	while(row=getRow()) {
//	    send("  \nstart a while iteration\n");
	   
	    if(row.key[1] == 0)
	    {
/*		send("key is 0, ");
		send("out is ");
		send(JSON.stringify(out));
		send("\n");

		ret = row.value.nodes;
		send("row[nodes] is ");
		send(JSON.stringify(ret));
*/
		if(out.length > 0)
		{
		    send(JSON.stringify(out.value));
		} 
		out=row;
	    } else {
/*		send("key is 1, ");
		send("out is ");
		send(JSON.stringify(out));
		send("\n");
		ret = out["nodes"];
		send("out[nodes] is ");
		send(JSON.stringify(ret)); */

		var missing=0;

		for(var i=0; i<out.value.nodes.length; ++i)
		{
/*
		    send("\n    begin inner for\n");
		    send(out.value.nodes[i].toString());
		    send(" - ")
		    send(row.value._id);
		    send(" ==? ");
		    send(out.value.nodes[i] == parseInt(row.value._id));
		    send("\n");

		    send("type is ");
//		    send(typeof(row.value.nodes[i]));
		    send("\n"); */

		    if(out.value.nodes[i] == parseInt(row.value._id))
		    {
			out.value.nodes[i] = row.doc;
		    }

		    if(parseInt(out.value.nodes[i]) == out.value.nodes[i])
			++missing;

		} 		
/*		send("\n    end inner for, ");
		send(missing.toString());
		send(" missing.\n"); */

		if(missing == 0)
		{
		    send(JSON.stringify(out.value));
		    out = {};
		}
	    }
//	    send("  \nend if w/p\n");
	}
/*	send("\nend outer for\n");
	send("out is ");
	send(JSON.stringify(out));
	send("\nout length is ");
	send(out.length);
*/
	if(out.length > 0)
	{
	    send(JSON.stringify(out.value));
	} 
    }); 
}

