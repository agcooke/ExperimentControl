from subprocess import Popen
import logging
import signal
class ARListener(object):
    """
    Used to start and stop the ant plus listener
    """
    def __init__(self,outfile,runName,videoDevice):
        self.processString = \
            ['roslaunch',
            'ar_sofiehdfformat_bridge',
            'simple_bridge.launch',
            'filename:='+outfile, 
            'runname:='+runName, 
            'videodevice:='+videoDevice, 
            ];
        

    def __del__(self):
        pass
    def open(self):
        #Setup the logger:
        logging.debug('Executing command: '+str(self.processString))    
        self.process = Popen(self.processString)

    def sync(self):
        #Setup the logger:
        pass

    def close(self):
        self.process.terminate()