import couchdb

db = None
db_name = ""
level="1"

def init(db, lv):
    global level, db_name
    db_name = db
    level = lv

def complete_name(level) :
    return "%s_%s"%(db_name, level)

def server():
    server = couchdb.Server(url="http://localhost:5984")
#    server.resource.credentials = ('root', 'j3onSUsd')
    return server

def dropdb(level):
    try:
        del server()[complete_name(level)]
    except couchdb.http.ResourceNotFound:
        pass

def connect(level):
    #server = couchdb.Server(url="http://gi88.geoinfo.tuwien.ac.at:5986")
    name = complete_name(level)
    try:
        return server().create(name)
    except couchdb.PreconditionFailed:
        return server()[name]

def getdb():
    global db
    if db:
        return db
    else:
        db = connect(level)
        return db
