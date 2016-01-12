
from imposm.parser import OSMParser
from os.path import basename, splitext
import couchdb
import client

class ImportDB(object):

    level=1

    def __init__(self, drop=True, buffer_size=10000):
        self.buffer_size=buffer_size
        self.drop=drop
        self.buf=[]
        self.buffered_coords=set()
        self.buffered_nodes=set()
        self.pushed_coords=set()
        self.pushed_nodes=set()
        self.nodecount = self.waycount = self.coordcount = 0

    def __call__(self, filename):

        client.init(splitext(basename(filename))[0], self.level)
        
        if(self.drop):
            client.dropdb(self.level)
            
        p = OSMParser(concurrency=4, 
                      ways_callback=self.way,
                      coords_callback=self.coord,
                      nodes_callback=self.node,
                      relations_callback=self.relation)
        p.parse(filename)
        self.flush_buffer()
        

    def id(self, osmid):
        return "%d"%osmid

    def processed_coord(self, osmid):
        global buffered_coords, pushed_coords
        if osmid in self.buffered_coords or osmid in self.pushed_coords:
            return True
        else:
            return False

    def buffered_coord(self, osmid):
        if osmid in self.buffered_coords:
            return True
        else:
            return False

    def unbuffer_coord(self, osmid):
        self.buffered_coords.remove(osmid)

    def processed_node(self, osmid):
        return osmid in self.buffered_nodes or osmid in self.pushed_nodes

    def put_buffer(self, item, is_coord=False, is_node=False):
        self.buf.append(item)
        if len(self.buf)>=self.buffer_size:
            self.flush_buffer()

    def flush_buffer(self):
        try:
            client.getdb().update(self.buf)
        except couchdb.ServerError:
            print self.buf
        self.buf=[]

    def add_tags(self, m,tags):
        tagsd = dict()
        for k,v in tags.iteritems():
            if k != '__tag_dummy__':
                if type(v) == str:                
                    tagsd[k] = v.lstrip('_')
                else:
                    tagsd[k] = v
                    m['tags']=tagsd

    def way(self, ways):
        for osmid, tags, nodes in ways:
            self.waycount+=1
            m = {'osmid': id(osmid),
                 '_id': id(osmid),
                 'type' : 'way',
                 'nodes': nodes}
            self.add_tags(m,tags)
            self.put_buffer(m)

    def node(self, nodes):    
            
        for osmid, tags, coords in nodes:
            self.nodecount+=1
            m = dict()
            m['type'] = 'node'
            m['_id'] = id(osmid)
            m['osmid'] = id(osmid)
            m['coords'] = coords
            self.add_tags(m,tags)

            if self.buffered_coord(id(osmid)):
                self.unbuffer_coord(id(osmid))
            elif self.processed_coord(id(osmid)):
                # this is a potential bottleneck because
                # we need to retrieve individual documents.
                # if this turns out to be a problem, we
                # must buffer delete operations as well
                client.getdb().delete(id(osmid))
                self.put_buffer(m,False,True)

    def coord(self, coords):

        for osmid, longitude, latitude in coords:
            self.coordcount+=1
            if not self.processed_node(id(osmid)):
                self.put_buffer({'osmid':id(osmid),
                                 '_id': id(osmid),
                                 'type':'node',
                                 'coords':[longitude,latitude]},True)

    def relation(self, relations):
        for osmid, tags, rels in relations:
            m = dict()
            m['type']='relation'
            m['osmid']=id(osmid)
            m['_id'] = id(osmid)
            m['members']=rels
            self.add_tags(m,tags)
            self.put_buffer(m)

    # this is a stupid trick to ensure we don't have to deal
    # with coords, but only with nodes...
    def add_dummy_filter(self, tags):
        tags['__tag_dummy__']='foo'
