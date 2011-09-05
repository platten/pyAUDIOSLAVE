#!/usr/bin/env python
import os
import sys
from subprocess import call

def main(fileList):
    for filename in fileList:
        retcode = call("/usr/bin/jsonlint " + filename, shell=True)
        if retcode ==  0:
            print "%s ok" % filename
        else:
            print "%s failed" % filename

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "./mongoverifier.py <export file 1>  [<export file 2> ...]"
        sys.exit(1)
    fileList = filter(os.path.exists, sys.argv[1:]) 
    main(fileList)
    sys.exit(0)

