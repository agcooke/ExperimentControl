import logging
import logging
import sys
settings={
'DEBUGLEVEL':logging.WARNING,
'DEBUGSTREAMOUT':sys.stdout,
'DEBUGFORMAT':'%(name)s->%(filename)s:%(funcName)s:%(lineno)d|%(levelname)s=>%(message)s',
}

def setLogger(DEBUGLEVEL=settings['DEBUGLEVEL'],FORMAT=settings['DEBUGFORMAT'],
    DEBUGSTREAM=settings['DEBUGSTREAMOUT']):
    logging.basicConfig(level=DEBUGLEVEL,
        format=FORMAT,
        stream=DEBUGSTREAM
        )
