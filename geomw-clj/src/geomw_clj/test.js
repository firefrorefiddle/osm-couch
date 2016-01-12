var jstream = require("JSONStream")
  , request = require("request")
  , es = require("event-stream")
  , http = require("http");

function completeWay(way, callback) {
    var outstanding = way.nodes.length;
    var data = [];

    for(i=0; i<way.nodes.length; i++) {
	var url = "http://localhost:5984/saalfelden_1/"+way.nodes[i];
	request({url: url},
		function(err, res) {
		    if(err) console.error(err);
		    data.push(JSON.parse(res.body).coords);
		    outstanding--;
		    if(outstanding == 0) {
			way.nodes = data;
			callback(null, JSON.stringify(way));
		    }
		});
    }
}

http.globalAgent.maxSockets = 1000;

var server = http.createServer(
    function(req, response) {
	request({url: "http://localhost:5984/saalfelden_1/_design/osmcouch/_view/ways"})
	    .pipe(jstream.parse("rows.*.value"))
	    .pipe(es.map(completeWay))
	    .pipe(response);	
    }).listen(3001, function() {
	console.log("Listening!");
    });
    

