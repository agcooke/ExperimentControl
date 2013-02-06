__author__="cooke"
__date__ ="$02-Feb-2012 15:26:23$"
import logging
import os
from subprocess import Popen
import tempfile
from experimentcontrol.core.InertiaTechnologySocketDriver import InertiaTechnologySocketDriver
from sofiehdfformat.core.SofieFileUtils import importdata
NETKEY = '\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'
TMPLOGFILE='tmp-output.csv';
IMURUNEXTENSION='/imu'
IMUPORT=1234
IMUHOST='127.0.0.1'
class IntertiaTechnologyListener(object):
    """
    Listener for the Inertia Technology IMU. One needs to install the PromoveGUI to be able to get this
    working.
    """
    def __init__(self,outfile,runName,serial,port=IMUPORT,host=IMUHOST):
        self.processString = ['/usr/bin/ProMoveGUI','-p 1234'];
        self.driver = InertiaTechnologySocketDriver(
            host=host,port=port,device=serial,
            mode='w')
        self.outfile = outfile;
        self.runName = runName+IMURUNEXTENSION;
        
        self.tmpdir = tempfile.mkdtemp()
        self.tmplogfile = os.path.join(self.tmpdir, TMPLOGFILE)
    def __del__(self):
        self.driver.close();
        self.process.terminate()


    def open(self):
        logging.debug('Executing command: '+str(self.processString))    
        self.process = Popen(self.processString)
        #Setup the logger:
        logging.debug('Opening Socket')
        self.driver.open();

        self.driver.startRecording(self.tmplogfile);

    def sync(self):
        #Setup the logger:
        self.driver.rtcTrigger();


    def close(self):
        self.driver.stopRecording();
        if os.path.isfile(self.tmplogfile):
            importdata(self.tmplogfile,
                self.outfile,
                self.runName,
                'description',
                True,
                False)
        if os.path.isfile(self.tmplogfile):
            os.remove(self.tmplogfile)
        if os.path.isdir(self.tmpdir):
            os.rmdir(self.tmpdir)
        self.process.terminate()