import datetime
import logging
import time

from sofiehdfformat.antparser.AntParser import parse_sample as ant_sample
from sofiehdfformat.antparser.AntParser import parse_sample_interpret as ant_sample_interpret
from sofiehdfformat.antpytableaccess.AntPyTableAccess import AntParsedDataAccess
from sofiehdfformat.antpytableaccess.AntPyTableAccess import AntRawDataAccess
import sofiehdfformat.core.SofieHdfFormatExceptions as exceptions
from sofiehdfformat.core.config import SPARKSUBDIRECTORY

EVENT_OPEN = '0-LOGOPEN'
EVENT_CLOSE = '1-LOGCLOSE'
EVENT_READ = '2-LOGREAD'
EVENT_WRITE = '3-LOGWRITE'

class LogWriter(object):
    def __init__(self, filename='',run='test'):
        self.is_open = False
        self.open(filename,run)

    def __del__(self):
        if self.is_open:
            self.fd.close()
            self.fdP.close()

    def open(self, filename='',run='test'):
        if filename == '':
            filename = datetime.datetime.now().isoformat() + '.h5'
        self.filename = filename

        if self.is_open == True:
            self.close()

        self.fd = AntRawDataAccess(filename,run+'/'+SPARKSUBDIRECTORY)
        self.fdP = AntParsedDataAccess(filename,run+'/'+SPARKSUBDIRECTORY)

        self.is_open = True
        #TODO write meta information...
        
    def close(self):
        if self.is_open:
            self.fd.close()
            self.fdP.close()
            self.is_open = False

    def _logEvent(self, event, data=None):
        timestamp = int(time.time())
        if event == EVENT_READ:
            information = {'packet':data,'timestamp':timestamp}
            try:
                informationRaw = ant_sample(information)
                logging.debug(informationRaw)
                informationParsed = ant_sample_interpret(informationRaw)
                self.fd.write(informationRaw)
                self.fdP.write(informationParsed)
            except exceptions.UnknownParseError,e:
                logging.debug('Error parsing sample:'+e.message)
        else:
            print event

    def logOpen(self):
        self._logEvent(EVENT_OPEN)

    def logClose(self):
        self._logEvent(EVENT_CLOSE)

    def logRead(self, data):
        self._logEvent(EVENT_READ, data)

    def logWrite(self, data):
        self._logEvent(EVENT_WRITE, data)
