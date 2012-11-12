import logging
import os
import socket
from time import sleep
class InertiaTechnologySocketDriver (object):
    def __init__(self,host='127.0.0.1',port=1234,device='/dev/ttyUSB0',
        mode='+'):
        '''
            Intialise the Driver.

            mode= + = autonumber file, a = append file, w = overwrite file
        '''
        self.is_open = False
        self.host = host
        self.port = int(port)
        self.device = device
        self.mode = mode
        #self.open()

    def __del__(self):
            self.close()
        
    def open(self):
        logging.debug('Opening socket')
        while self.is_open == False:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                #if self.is_open == True:
                #    self.close()
                self.is_open = True
            except socket.error:
                logging.debug('RETRYING TO OPEN CONNECTION.')
                sleep(0.5)

    def close(self):
        
        if self.is_open:
            try:
                self.stopRecording()
                self.socket.close()
            except socket.error:
                print 'IMU CLOSED and DELETED'
            self.is_open = False

    def _writeCommand(self, command):
        self.socket.sendall(command)

    def startRecording(self,logFilename):
        logging.debug('SENDING START COMMAND TO GUI')
        if self.mode == '+':
            existBehaviour = 2;
        elif self.mode == 'a':
            existBehaviour = 1;
        else:
            existBehaviour = 0
        if os.path.isfile(logFilename):
            os.unlink(logFilename)
        CMD='open {0} -l {1}  --existBehaviour {2}\n'.format(self.device,
            logFilename,
            existBehaviour)

        logging.debug(CMD)
        self._writeCommand(CMD)
        sleep(0.5)
        logging.debug('Setting RTC');
        self.setRtc()
        sleep(0.5)
        logging.debug('Enabling external triggers');
        self.enableExternalRtcTrigger()

    def stopRecording(self):
        CMD='close {0}\n'.format(self.device)
        self._writeCommand(CMD)

    def enableExternalRtcTrigger(self):
        CMD='set RTCConfig --externalTrigger=true --enableSampling=false\n'
        self._writeCommand(CMD)

    def rtcTrigger(self):
        CMD='cmd ServiceSendEvent --sampler 9 --event 1\n'
        self._writeCommand(CMD)
    
    def setRtc(self):
        CMD='cmd ServiceSetRTC\n'
        self._writeCommand(CMD)
