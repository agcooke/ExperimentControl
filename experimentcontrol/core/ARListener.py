from subprocess import Popen
import logging
import roslib; roslib.load_manifest('sofiehdfformat_rosdriver')
from sofiehdfformat_rosdriver.import_csv_data import importARData

SMALLMARKER=58.7
BIGMARKER=97.0

class ARListener(object):
    """
    Used to start and stop the ant plus listener
    """
    def __init__(self,outfile,runName,videoDevice,highRes=False,markerSize=SMALLMARKER):
        if highRes == False:
            launchFile = 'simple_bridge_normal.launch'
        else:
            launchFile = 'simple_bridge_1920.launch'
        self.filename = outfile
        self.runName = runName+'/ar'
        self.processString = \
            ['roslaunch',
            'sofiehdfformat_rosdriver',
            launchFile,
            'filename:='+self.filename,
            'runname:='+self.runName,
            'videodevice:='+videoDevice,
            'markersize:='+str(markerSize),
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
        importARData(self.filename,self.runName)
        self.process.terminate()
        