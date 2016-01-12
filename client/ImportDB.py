
from imposm.parser import OSMParser
from os.path import basename, splitext
import couchdb
import client

def mkid(osmid):
    """Convert the OSM Id to a CouchDB id.
    Currently, this is the same as str"""
    return "%d"%osmid

def add_tags(m, tags):
    """Add tags to an element"""
    tagsd = dict()
    for k,v in tags.iteritems():
        if k != '__tag_dummy__':
            if type(v) == str:                
                tagsd[k] = v.lstrip('_')
            else:
                tagsd[k] = v
    m['tags']=tagsd
    return m

def mk_way(osmid, tags, nodes):
    m = {'osmid': mkid(osmid),
         '_id': mkid(osmid),
         'type' : 'way',
         'nodes': nodes}
    add_tags(m,tags)
    return m


def mk_coord(osmid, longitude, latitude):
    return {'osmid':mkid(osmid),
            '_id': mkid(osmid),
            'type':'node',
            'coords':[longitude,latitude]}

def mk_relation(osmid, tags, relations):
    m = dict()
    m['type']='relation'
    m['osmid']=mkid(osmid)
    m['_id'] = mkid(osmid)
    m['members']=relations
    add_tags(m,tags)
    return m

def mk_node(osmid, tags, coords):
    m = dict()
    m['type'] = 'node'
    m['_id'] = mkid(osmid)
    m['osmid'] = mkid(osmid)
    m['coords'] = coords
    add_tags(m,tags)
    return m

# this is a stupid trick to ensure we don't have to deal
# with coords, but only with nodes...
def add_dummy_filter(tags):
    tags['__tag_dummy__']='foo'



## class for importing osm.pbf into couchdb.
## this is intended to be subclassed by a 
## specific level
##
## The subclass should specify the correct level
## and override those operations which differ from
## plain-and-simple insertion
class ImportDB(object):

    level = 0

    def __init__(self, level, drop=True, buffer_size=10000):
        self.level = level
        self.buffer_size = buffer_size
        self.drop = drop
        self.buf = []
        self.buffered_coords = set()
        self.buffered_nodes = set()
        self.pushed_coords = set()
        self.pushed_nodes = set()
        self.nodecount = self.waycount = self.coordcount = 0

    def __call__(self, filename):

        client.init(splitext(basename(filename))[0], self.level)

        if self.drop:
            client.dropdb(self.level)

        parser = OSMParser(concurrency=4,
                           ways_callback=self.way,
                           coords_callback=self.coord,
                           nodes_callback=self.node,
                           relations_callback=self.relation)
        parser.parse(filename)
        self.flush_buffer()

    def processed_coord(self, osmid):
        """True if a coord has already been processed, false otherwise"""
        if osmid in self.buffered_coords or osmid in self.pushed_coords:
            return True
        else:
            return False

    def buffered_coord(self, osmid):
        """True if a coord is currently buffered, false otherwise"""
        if osmid in self.buffered_coords:
            return True
        else:
            return False

    def unbuffer_coord(self, osmid):
        """Remove a coord from the buffer"""
        self.buffered_coords.remove(osmid)

    def processed_node(self, osmid):
        """True if a node has already been processed, false otherwise"""
        return osmid in self.buffered_nodes or osmid in self.pushed_nodes

    def put_buffer(self, item):
        """Add something to the buffer"""
        self.buf.append(item)
        if len(self.buf)>=self.buffer_size:
            self.flush_buffer()

    def flush_buffer(self):
        """Send the contents of the buffer to the server and clear it."""
        try:
            client.getdb().update(self.buf)
        except couchdb.ServerError:
            print self.buf
        self.buf=[]

    def way(self, ways):
        """Convert a way and put it into the buffer"""
        for osmid, tags, nodes in ways:
            self.waycount+=1
            self.put_buffer(mk_way(osmid, tags, nodes))

    def node(self, nodes):    
        """Convert a node and put it into the buffer. If it turns
           out that this was already processed as a coord then 
           delete the coord from the buffer or db."""
        for osmid, tags, coords in nodes:
            self.nodecount+=1
            m = mk_node(osmid, tags, coords)

            if self.buffered_coord(mkid(osmid)):
                self.unbuffer_coord(mkid(osmid))
            elif self.processed_coord(mkid(osmid)):
                # this is a potential bottleneck because
                # we need to retrieve individual documents.
                # if this turns out to be a problem, we
                # must buffer delete operations as well
                client.getdb().delete(mkid(osmid))
                self.put_buffer(m)

    def coord(self, coords):
        """Convert a coord and buffer it as a node."""
        for osmid, longitude, latitude in coords:
            self.coordcount+=1
            if not self.processed_node(mkid(osmid)):
                self.put_buffer(mk_coord(osmid, longitude, latitude))

    def relation(self, relations):
        """Convert a relation and buffer it"""
        for osmid, tags, rels in relations:
            self.put_buffer(mk_relation(osmid, tags, rels))

