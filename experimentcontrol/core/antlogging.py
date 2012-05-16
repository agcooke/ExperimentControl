import logging
import sys
settings={
'DEBUGLEVEL':logging.DEBUG,
'DEBUGSTREAMOUT':sys.stdout,
'DEBUGFORMAT':'%(name)s->%(filename)s:%(funcName)s:%(lineno)d|%(levelname)s=>%(message)s',
}

def setLogger(DEBUGLEVEL=settings['DEBUGLEVEL'],FORMAT=settings['DEBUGFORMAT'],
    DEBUGSTREAM=settings['DEBUGSTREAMOUT']):
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter(FORMAT)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    return ch