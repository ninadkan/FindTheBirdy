

import logging 
import sys

def get_logger(level):
    azure_logger = logging.getLogger("azure.processorhost")
    azure_logger.setLevel(level)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s'))
    if not azure_logger.handlers:
        azure_logger.addHandler(handler)

    uamqp_logger = logging.getLogger("uamqp")
    uamqp_logger.setLevel(level)
    if not uamqp_logger.handlers:
        uamqp_logger.addHandler(handler)
    return azure_logger
