from imposm.parser import OSMParser
import sys
from os.path import basename, splitext, isfile
import os
import couchdb
import bsddb
from client import getdb, init, dropdb

buffer_size=10000
nodedb_name = '/tmp/nodes.db'
node_way_db_name = '/tmp/nodes_ways.db'

def importdb(filename):
    global buf, buffered_coords, buffered_nodes, pushed_coords, pushed_nodes
    buf=[]
    buffered_coords=set()
    buffered_nodes=set()
    pushed_coords=set()
    pushed_nodes=set()
    global waycount, nodecount, coordcount
    nodecount = waycount = coordcount = 0

    global nodedb, node_way_db
    if isfile(nodedb_name):
        os.remove(nodedb_name)
    if isfile(node_way_db_name):
        os.remove(node_way_db_name)

    nodedb = bsddb.hashopen(nodedb_name, 'c')
    node_way_db = bsddb.hashopen(node_way_db_name, 'c')
    
    p = OSMParser(concurrency=4, 
                  ways_callback=way,
                  coords_callback=coord,
                  nodes_callback=node,
                  relations_callback=relation)
    p.parse(filename)
    
    for n, ws in node_way_db.iteritems():
        try:
            val = eval(nodedb[n])
            for w in eval(ws):
                val['ways'].append(w)
            nodedb[n] = str(val) 
        except KeyError:
            pass
#                print "Warning: Key %s not found in nodedb"%n

    for n in nodedb.itervalues():
        put_buffer(eval(n), False, True)

    flush_buffer()

def processed_coord(osmid):
    global buffered_coords, pushed_coords
    if osmid in buffered_coords or osmid in pushed_coords:
        return True
    else:
        return False

def buffered_coord(osmid):
    global buffered_coords
    if osmid in buffered_coords:
        return True
    else:
        return False

def unbuffer_coord(osmid):
    global buffered_coords
    buffered_coords.remove(osmid)

def processed_node(osmid):
    global buffered_nodes, pushed_nodes
    if osmid in buffered_nodes or osmid in pushed_nodes:
        return True
    else:
        return False

def put_buffer(item, is_coord=False, is_node=False):

    global buf #, buffered_coords, buffered_nodes

    buf.append(item)

#    if is_coord:
#        buffered_coords.add(item['osmid'])
#    elif is_node:
#        buffered_nodes.add(item['osmid'])

    if len(buf)>=buffer_size:
        flush_buffer()

def flush_buffer():
    global buf 

    try:    getdb().update(buf)
    except couchdb.ServerError:
        print buf
    buf=[]

#, pushed_coords, pushed_nodes
#    global buffered_coords, buffered_nodes


    buf=[]
 #   pushed_coords=pushed_coords.union(buffered_coords)
 #   pushed_nodes=pushed_nodes.union(buffered_nodes)
 #   buffered_coords=set()
 #   buffered_nodes=set()    

def add_tags(m,tags):
    tagsd = dict()
    for k,v in tags.iteritems():
        if k != '__tag_dummy__':
            if type(v) == str:                
                tagsd[k] = v.lstrip('_')
            else:
                tagsd[k] = v
    m['tags']=tagsd

def way(ways):

    global waycount

    for osmid, tags, nodes in ways:
        waycount+=1
        m = {'osmid': str(osmid),
             '_id': str(osmid),
             'type' : 'way',
             'nodes': nodes}

        for n in nodes:
            if node_way_db.has_key(str(n)):
                val = eval(node_way_db[str(n)])
                val.append(str(osmid))
                node_way_db[str(n)]= str(val)
            else:
                node_way_db[str(n)] = str([str(osmid)])

        add_tags(m,tags)
        put_buffer(m)

def node(nodes):

    global nodecount
    for osmid, tags, coords in nodes:
        nodecount+=1
        m = dict()
        m['type'] = 'node'
        m['_id'] = str(osmid)
        m['osmid'] = str(osmid)
        m['coords'] = coords
        m['ways'] = []
        add_tags(m,tags)
        nodedb[str(osmid)] = str(m)

def coord(coords):

    global coordcount
    for osmid, longitude, latitude in coords:
        coordcount+=1
        if not nodedb.has_key(str(osmid)):
            nodedb[str(osmid)] = str({'osmid':str(osmid),
                                      '_id': str(osmid),
                                      'type': 'node',
                                      'ways': [],
                                      'coords': [longitude,latitude]})
    
def relation(relations):
    for osmid, tags, rels in relations:
        m = dict()
        m['type']='relation'
        m['osmid']=str(osmid)
        m['_id'] = str(osmid)
        m['members']=rels
        add_tags(m,tags)
        put_buffer(m)

# this is a stupid trick to ensure we don't have to deal
# with coords, but only with nodes...
def add_dummy_filter(tags):
    tags['__tag_dummy__']='foo'


if __name__ == "__main__":
    def usage():
        print "usage: importdb <file>"
        
    if (len(sys.argv) < 2):
        usage()
    elif not isfile(sys.argv[1]):
        usage()
    else:
        init(splitext(basename(sys.argv[1]))[0], 2)
        dropdb(2)
        importdb(sys.argv[1])
        print "Ways: %d Nodes: %d Coords: %d"%(waycount, nodecount, coordcount)
