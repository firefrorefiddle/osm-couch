import sys
from os.path import isfile
from client.ImportDB import ImportDB

class ImportDB_1(ImportDB):
    def __init__(self, drop=True, bufferSize=100000):
        ImportDB.__init__(self, drop, bufferSize)

    def __call__(self, filename):
        ImportDB.__call__(self, filename)

if __name__ == "__main__":
    def usage():
        print "usage: importdb <file>"
        
    if (len(sys.argv) < 2):
        usage()
    elif not isfile(sys.argv[1]):
        usage()
    else:
        imp = ImportDB_1()
        imp(sys.argv[1])
        print "Ways: %d Nodes: %d Coords: %d"%(imp.waycount, imp.nodecount, imp.coordcount)
