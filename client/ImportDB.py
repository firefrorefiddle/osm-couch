
from imposm.parser import OSMParser
from os.path import basename, splitext
import couchdb
import client
from client.BSDBuf import BSDBuf

# this is a stupid trick to ensure we don't have to deal
# with coords, but only with nodes...
def add_dummy_filter(tags):
    tags['__tag_dummy__']='foo'


def mkid(osmid):
    """Convert the OSM Id to a CouchDB id.
    Currently, this is the same as str"""
    return "%d"%osmid


class ImportDB(object):
    """class for importing osm.pbf into couchdb.
    is intended to be subclassed by a level.

    subclass should specify the correct level
    override those operations which differ from
    -and-simple insertion"""

    level = 0

    def __init__(self, level, drop=True, buffer_size=10000):

        self.level = level
        self.buffer_size = buffer_size
        self.drop = drop
        self.buf = {
            "nodes": BSDBuf(),
            "coords": BSDBuf(),
            "ways": BSDBuf(),
            "relations": BSDBuf()
        }
        self.counts = {
            "nodes": 0,
            "ways": 0,
            "relations": 0
        }

    def flush_buffer(self):
        """Send the contents of the buffer to the server and clear it."""
        try:
            for buf in self.buf.itervalues():
                client.getdb().update(list(buf.itervalues()))
        except couchdb.ServerError:
            print self.buf
        self.buf=[]

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

    def add_tags(self, m, tags):
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

    def count(self, cat):
        self.counts[cat] += 1

    def mk_way(self, osmid, tags, nodes):
        m = {'osmid': mkid(osmid),
             '_id': mkid(osmid),
             'type' : 'way',
             'nodes': nodes}
        self.add_tags(m,tags)
        return m

    def mk_coord(self, osmid, longitude, latitude):
        return {'osmid':mkid(osmid),
                '_id': mkid(osmid),
                'type':'node',
                'coords':[longitude,latitude]}

    def mk_relation(self, osmid, tags, relations):
        m = dict()
        m['type']='relation'
        m['osmid']=mkid(osmid)
        m['_id'] = mkid(osmid)
        m['members']=relations
        self.add_tags(m,tags)
        return m

    def mk_node(self, osmid, tags, coords):
        m = dict()
        m['type'] = 'node'
        m['_id'] = mkid(osmid)
        m['osmid'] = mkid(osmid)
        m['coords'] = coords
        self.add_tags(m,tags)
        return m

    def node_hook(self, node):
        return node

    def coord_hook(self, node):
        return node

    def way_hook(self, node):
        return node

    def relation_hook(self, node):
        return node

    def pre_server_hook(self):
        pass

    def way(self, ways):
        """Convert a way and put it into the buffer"""
        for osmid, tags, nodes in ways:
            self.count("ways")
            self.buf["ways"][osmid] = self.way_hook(self.mk_way(osmid, tags, nodes))

    def node(self, nodes):    
        """Convert a node and put it into the buffer. If it turns
           out that this was already processed as a coord then 
           delete the coord from the buffer or db."""
        for osmid, tags, coords in nodes:
            self.count("nodes")
            self.buf["nodes"][osmid] = self.node_hook(self.mk_node(osmid, tags, coords))

    def coord(self, coords):
        """Convert a coord and buffer it as a node."""
        for osmid, longitude, latitude in coords:
            self.count("nodes")
            self.buf["coords"][osmid] = self.coord_hook(self.mk_coord(osmid, longitude, latitude))

    def relation(self, relations):
        """Convert a relation and buffer it"""
        for osmid, tags, rels in relations:
            self.count("relations")
            self.buf["relations"][osmid] = self.relation_hook(self.mk_relation(osmid, tags, rels))
