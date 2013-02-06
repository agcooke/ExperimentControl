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
    """ This provides a writer to the SOFIE HDF FORMAT system. Use with caution, Pytables
    does not support concurrent writes to an HDF file. (Currently not used in the ExperimentControl Package.)"""
    
    previousParsedValue = None;

    def __init__(self, filename='',runName='test'):
        self.is_open = False
        self.open(filename,runName)

    def __del__(self):
        if self.is_open:
            self.fd.close()
            self.fdP.close()

    def open(self, filename='',runName='test'):
        if filename == '':
            filename = datetime.datetime.now().isoformat() + '.h5'

        if self.is_open == True:
            self.close()

        self.fd = AntRawDataAccess(filename,runName+'/'+SPARKSUBDIRECTORY)
        self.fdP = AntParsedDataAccess(filename,runName+'/'+SPARKSUBDIRECTORY)

        self.is_open = True
        #TODO write meta information...
        
    def close(self):
        if self.is_open:
            self.fd.close()
            self.fdP.close()
            self.is_open = False

    def _logEvent(self, event, data=None):
        timestamp = time.time()
        if event == EVENT_READ and len(data)>0:
            #logging.debug(len(data))
            information = {'packet':data,'timestamp':timestamp}
            try:
                #logging.debug(information)
                informationRaw = ant_sample(information)
                if informationRaw == []:
                    logging.debug('NOT A BROADCAST')
                    return
                logging.debug('Information Raw:'+str(informationRaw))
                informationParsed = ant_sample_interpret(informationRaw,\
                    self.previousParsedValue)
                self.previousParsedValue = informationParsed
                self.fd.write(informationRaw)
                self.fdP.write(informationParsed)
            except exceptions.UnknownParseError,e:
                pass
            except exceptions.ChecksumParseError,e:
                logging.debug('CHECKSUM ERROR:'+e.message)

    def logOpen(self):
        self._logEvent(EVENT_OPEN)

    def logClose(self):
        self._logEvent(EVENT_CLOSE)

    def logRead(self, data):
        self._logEvent(EVENT_READ, data)

    def logWrite(self, data):
        self._logEvent(EVENT_WRITE, data)

    def sync(self):
        self.fd.writeSync();
