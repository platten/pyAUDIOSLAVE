#!/usr/bin/python

from tasks import *
import os, sys
from magic import Magic
from pyaudioslave.config import SUPPORTED_TYPES

def returnType(filePath):
    if not filePath:
        filePath = self.sourcefile
        
    m = Magic()
    filetype =  m.from_file(filePath)
    for mediatype in SUPPORTED_TYPES.keys():
        for filestring in SUPPORTED_TYPES[mediatype]:
            if filestring in filetype:
                return mediatype
    return None

def walker (rootDir):
    fileList = []
    rootDir = os.path.abspath(rootDir)
    for root, dirs, files in os.walk(rootDir):
        for name in files:
            filePath = os.path.join(root, name)
            if os.path.isfile(filePath):
                try:
                    type = returnType(os.path.abspath(filePath))
                except:
                    continue
                if type:
                    fileList.append(filePath)
    
    return fileList

def recursiveTranscoder(rootDir, destRoot, destFormat):
    fileList = walker(rootDir)
    fileDict = {}
    for path in fileList:
        destPath = os.path.abspath(os.path.join(destRoot, os.path.relpath(path, rootDir)))
        destPath = os.path.splitext(destPath)[0] + '.' + destFormat
        
        if destPath in fileDict.values():
            continue
        fileDict[path] = destPath
    
    for key in fileDict.keys():
        transcode.delay(key, fileDict[key], destFormat)
        print "Encode job for '%s' added" % key
    print "done"


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "./populator.py <source_root_dir> <dest_root_dir> {%s}" % ", ".join(SUPPORTED_TYPES.keys())
        sys.exit(1)
    recursiveTranscoder(sys.argv[1], sys.argv[2], sys.argv[3])
    print "Jobs added."
    sys.exit(0)