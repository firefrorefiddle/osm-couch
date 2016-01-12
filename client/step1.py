from client import getdb
import sys

batchsize=4000

def nodeView():
    return getdb().view("osmcouch/nodes")

def lookupNode(n):
    return nodeView()[n]

def wayView():
    return getdb().view("osmcouch/nodes")

def ways():
    return getdb().iterview("osmcouch/ways", batchsize)

def ways_with_nodes():
    for row in ways():
        nodeids = row.value['nodes']
        row.value['nodes'] = map(lambda n: getdb()[str(n)], nodeids)
        yield row

def main():

    def usage():
        print "Usage: %s helpful message"%sys.argv[0]

    if len(sys.argv) < 2:
        usage()
    else:
        src=None
        mode = sys.argv[1]

        if mode == "ways":
            src = ways()
        elif mode == "ways+":
            src = ways_with_nodes()
        
        if src == None:
            usage()
        else:
            for row in src:
                print row

if __name__ == "__main__":
    main()
