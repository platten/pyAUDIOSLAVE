#!/usr/bin/env python
from pymongo import Connection
import json
import sys
import codecs
import os
import demjson
from subprocess import call

def id_stripper(dictItem):
    del dictItem['_id']
    return dictItem

def main(exportLocation):
    connection = Connection()
    
    db = connection.echoprint_codegen
    mongodbcursor = db.posts.find()
    count = 0
    lineending = 0
    outfile = codecs.open(exportLocation + str(lineending), 'w',  "utf8")
    outfile.write(u'[\n')
    
    for line in mongodbcursor:
        if count:
            outfile.write(u',\n')
        outfile.write(demjson.encode(id_stripper(line), strict=True, compactly=True, escape_unicode='False', encoding='utf-8'))
        count += 1
        startcomma = True
        if not count % 100:
            if os.path.getsize(exportLocation + str(lineending)) > 500000000:
                outfile.write(u'\n]\n')
                outfile.close()
                lineending += 1
                outfile = codecs.open(exportLocation + str(lineending), 'w',  "utf8")
                outfile.write(u'[\n')
                count = 0
    outfile.write(u']\n')
    outfile.close()
    print "Done writing, time for sanity check"
   
    if not os.path.exists('/usr/bin/jsonlint'):
        print "jsonlint not found, will not check if files are valid"
        sys.exit(1)
 
    for suffix in range(0, lineending + 1):
        retcode = call("/usr/bin/jsonlint" + " %s%s" % (exportLocation, str(suffix)), shell=True)
        if retcode ==  0:
            print "%s%s ok" % (exportLocation, str(suffix))
        else:
            print "%s%s failed" % (exportLocation, str(suffix))

    print "Sanity test passed"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "./mongoexporter.py <export file>" 
        sys.exit(1)
    main(sys.argv[1])
    sys.exit(0)
