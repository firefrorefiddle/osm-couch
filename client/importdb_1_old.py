from imposm.parser import OSMParser
import sys
from os.path import basename, splitext, isfile
import couchdb
from client import getdb, init, dropdb

buffer_size=10000

def importdb(filename):
    global buf, buffered_coords, buffered_nodes, pushed_coords, pushed_nodes
    buf=[]
    buffered_coords=set()
    buffered_nodes=set()
    pushed_coords=set()
    pushed_nodes=set()
    global waycount, nodecount, coordcount
    nodecount = waycount = coordcount = 0

    p = OSMParser(concurrency=4, 
                  ways_callback=way,
                  coords_callback=coord,
                  nodes_callback=node,
                  relations_callback=relation)
    p.parse(filename)
    flush_buffer()

def id(osmid):
    return "%d"%osmid

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
        m = {'osmid': id(osmid),
             '_id': id(osmid),
             'type' : 'way',
             'nodes': nodes}
        add_tags(m,tags)
        put_buffer(m)

def node(nodes):

    global nodecount

    for osmid, tags, coords in nodes:
        nodecount+=1
        m = dict()
        m['type'] = 'node'
        m['_id'] = id(osmid)
        m['osmid'] = id(osmid)
        m['coords'] = coords
        add_tags(m,tags)

        if buffered_coord(id(osmid)):
            unbuffer_coord(id(osmid))
        elif processed_coord(id(osmid)):
            # this is a potential bottleneck because
            # we need to retrieve individual documents.
            # if this turns out to be a problem, we
            # must buffer delete operations as well
            db.delete(db[id(osmid)])
        put_buffer(m,False,True)

def coord(coords):
    global coordcount

    for osmid, longitude, latitude in coords:
        coordcount+=1
        if not processed_node(id(osmid)):
            put_buffer({'osmid':id(osmid),
                        '_id': id(osmid),
                        'type':'node',
                        'coords':[longitude,latitude]},True)

def relation(relations):
    for osmid, tags, rels in relations:
        m = dict()
        m['type']='relation'
        m['osmid']=id(osmid)
        m['_id'] = id(osmid)
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
        init(splitext(basename(sys.argv[1]))[0], 1)
        dropdb(1)
        importdb(sys.argv[1])
        print "Ways: %d Nodes: %d Coords: %d"%(waycount, nodecount, coordcount)
