__author__="cooke"
__date__ ="$02-Feb-2012 15:26:23$"

"""
Initialize a basic broadcast slave channel for listening to
an ANT+ Bicycle cadence and speed senser, using raw messages
and event handlers.

"""
import logging
import os
from subprocess import Popen

from experimentcontrol.core.InertiaTechnologySocketDriver import InertiaTechnologySocketDriver
from sofiehdfformat.core.SofieFileUtils import importdata
NETKEY = '\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'
TMPLOGFILE=os.path.abspath(os.path.join('.','tmp-output.csv'));
IMURUNEXTENSION='/imu'
class IntertiaTechnologyListener(object):
    """
    Used to start and stop the ant plus listener
    """
    def __init__(self,outfile,runName,port,host,serial):
        self.processString = ['/usr/bin/ProMoveGUI','-p 1234'];
        self.driver = InertiaTechnologySocketDriver(
            host=host,port=port,device=serial,
            mode='w')
        self.outfile = outfile;
        self.runName = runName+IMURUNEXTENSION;
    def __del__(self):
        self.driver.close();
        self.process.terminate()


    def open(self):
        logging.debug('Executing command: '+str(self.processString))    
        self.process = Popen(self.processString)
        #Setup the logger:
        logging.debug('Opening Socket')
        self.driver.open();

        self.driver.startRecording(TMPLOGFILE);

    def sync(self):
        #Setup the logger:
        self.driver.rtcTrigger();


    def close(self):
        self.driver.stopRecording();
        if os.path.isfile(TMPLOGFILE):
            importdata(TMPLOGFILE,
                self.outfile,
                self.runName,
                'description',
                True,
                False)
        self.process.terminate()