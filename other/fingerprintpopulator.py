#!/usr/bin/python

from tasks import *
import os, sys
from magic import Magic
from pyaudioslave.config import SUPPORTED_TYPES
from pprint import pprint

def walker (rootDir):
    fileList = []
    exts = map(lambda a: ".%s" % a, SUPPORTED_TYPES.keys())
    rootDir = os.path.abspath(rootDir)
    for root, dirs, files in os.walk(rootDir):
        for name in files:
            filePath = os.path.join(root, name)
            if os.path.isfile(filePath) and os.path.splitext(filePath)[1] in exts:
                fileList.append(filePath)
    
    return fileList

        
def recursiveCodegen(rootDir):
    fileList = walker(rootDir)
    for key in fileList:
        codegen.delay(key)
    print "done"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "./fingerprintpopulator.py <source_root_dir> " 
        sys.exit(1)
    recursiveCodegen (sys.argv[1])
    print "Jobs added."
    sys.exit(0)
