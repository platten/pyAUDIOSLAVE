from celery.task import task
from pyaudioslave import AudioSlave
from pymongo import Connection

@task
def add(x, y):
    logger = add.get_logger()
    logger.info("Adding %s + %s" % (x, y))
    return x + y


@task
def transcode(sourcefile, destinationPath, destFormat):
    logger = transcode.get_logger()
    logger.info("Source path : %s" % sourcefile)
    afile = AudioSlave(sourcefile)
    transcodedFile = afile.transcode(destFormat, destinationPath)
    logger.info("Transcoded path : %s" % transcodedFile)
    return transcodedFile

@task
def codegen(sourcefile, quickMode=False):
    logger = transcode.get_logger()
    logger.info("Source path : %s" % sourcefile)
    afile = AudioSlave(sourcefile, echoprint=True, echoprintQuickMode=quickMode)
    echoprintCode = afile.get_echoprint_code()[0]
    logger.info("Echoprint code extracted, saving to database")

    connection = Connection('localhost', 27017)
    db = connection.echoprint_codegen
    collection = db.echoprint_collection
    posts = db.posts
    oid = posts.insert(afile.get_echoprint_code()[0])
    logger.info("Object ID : %s" % oid)
    return oid