

import logging 
import sys


globalHandler = None
globalLoggingLevel = logging.INFO

def getGlobalHandler():
    global globalHandler
    
    if (globalHandler == None):
        globalHandler = logging.StreamHandler(stream=sys.stdout)
        globalHandler.setFormatter(logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s'))
    return globalHandler

def getGlobalLogObject(name):
    global globalLoggingLevel
    logObject = logging.getLogger(name)
    logObject.addHandler(getGlobalHandler())
    logObject.setLevel(globalLoggingLevel)
    return logObject

# Maintained for backward compatibility.
# TODO: Remove once not needed. 
def get_logger(level):
    handler = getGlobalHandler()
    azure_logger = logging.getLogger("eventProcessing")
    azure_logger.setLevel(level)

    if not azure_logger.handlers:
        azure_logger.addHandler(handler)

    # add uamqp
    uamqp_logger = logging.getLogger("uamqp")
    if (uamqp_logger):
        uamqp_logger.setLevel(level)
        if not uamqp_logger.handlers:
            uamqp_logger.addHandler(handler)

    # add unicorn
    gunicorn_logger = logging.getLogger("gunicorn")
    if (gunicorn_logger):
        gunicorn_logger.setLevel(level)
        if not gunicorn_logger.handlers:
            gunicorn_logger.addHandler(handler)
        
    return azure_logger


class clsLoggingBase:
    global globalLoggingLevel
    def __init__(self, name):
        self.logObj = logging.getLogger(name)
        self.logObj.addHandler(getGlobalHandler())
        self.logObj.setLevel(globalLoggingLevel)
        return

    def getLoggingObj(self):
        return self.logObj






