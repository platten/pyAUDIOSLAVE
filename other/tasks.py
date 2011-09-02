from celery.task import task
from pyaudioslave import AudioSlave
from pymongo import Connection

@task
def transcode(sourcefile, destinationPath, destFormat):
    logger = transcode.get_logger()
    logger.info("Source path : %s" % sourcefile)
    afile = AudioSlave(sourcefile)
    transcodedFile = afile.transcode(destFormat, destinationPath)
    logger.info("Transcoded path : %s" % transcodedFile)
    return transcodedFile

@task
def codegen(sourcefile):
    logger = transcode.get_logger()
    logger.info("Source path : %s" % sourcefile)
    afile = AudioSlave(sourcefile)
    echoprintCode = afile.get_echoprint_code()[0]
    
    connection = Connection('localhost', 27017)
    db = connection.echoprint_codegen
    collection = db.echoprint_collection
    posts = db.posts
    oid = posts.insert(afile.get_echoprint_code()[0])
    logger.info("Object ID : %s" % oid)
    return oid
