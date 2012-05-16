import socket
import time
from experimentcontrol.core.Exceptions import CouldNotConnectToSocket
class InertiaTechnologySocketDriver (object):
    def __init__(self,host='localhost',port=1234,device='/dev/ttyUSB0',
        mode='+'):
            '''
            Intialise the Driver.

            mode= + = autonumber file, a = append file, w = overwrite file
            '''
        self.is_open = False
        self.host = host
        self.port = port
        self.device = device
        self.open(filename,runName)
        self.mode = '+'

    def __del__(self):
        if self.is_open:
            self.fd.close()
            self.fdP.close()

    def open(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.device = device
        if not self.socket.connect((self.host, self.port)):
            raise CouldNotConnectToSocket()
        #if self.is_open == True:
        #    self.close()
        self.is_open = True
        

    def close(self):
        if self.is_open:
            self.stopRecording()
            self.socket.close()
            self.is_open = False

    def _writeCommand(self, command):
        self.socket.sendall(command)

    def startRecording(self,logFilename):
        if self.mode = '+':
            existBehaviour = 2;
        elif self.mode = 'a':
            existBehaviour = 1;
        else:
            existBehaviour = 0
        CMD='open %s -l %s  --existBehaviour %d',(self.device,
            logFilename,
            existBehaviour)
        self._writeCommand(CMD)

    def stopRecording(self):
        CMD='close %s',(self.device)
        self._writeCommand(CMD)




