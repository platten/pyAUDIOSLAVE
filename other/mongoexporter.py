#!/usr/bin/env python
from pymongo import Connection
import json

def id_stripper(dictItem):
    del dictItem['_id']
    return dictItem

def main(exportLocation):
    connection = Connection()
    
    db = connection.echoprint_codegen
    mongodbcursor = db.posts.find()
    count = 0
    
    outfile = open(exportLocation, 'w')
    outfile.write('[\n')
    
    for line in mongodbcursor:
        if count:
            outfile.write(',\n')
        outfile.write(json.dumps(id_stripper(line)))
        count += 1
        if not count % 1000:
            print "Exported %d entries" % count
    outfile.write(']\n')
    outfile.close()
    print "Done writing, time for sanity check"
    
    outfile = open(exportLocation, 'r')
    json.load(outfile)
    outfile.close()
    print "Sanity test passed"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "./mongoexporter.py <export file>" 
        sys.exit(1)
    main(sys.argv[1])
    sys.exit(0)