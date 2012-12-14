from subprocess import Popen
import logging
import time
import roslib; roslib.load_manifest('sofiehdfformat_rosdriver')
from sofiehdfformat_rosdriver.import_csv_data import importARData,importBagData
import os, tempfile
SMALLMARKER=58.7
BIGMARKER=97.0
ARRUNEXTENSION='/ar'
USBCAMERATOPIC='/usb_cam/image_raw'
USBCAMTMPFILE='usbcam.bag'
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
        
        self.tmpdir = tempfile.mkdtemp()
        self.usbCamBagFilename = os.path.join(self.tmpdir, USBCAMTMPFILE)
        
        self.runName = runName+ARRUNEXTENSION
        self.processString = \
            ['roslaunch',
            'sofiehdfformat_rosdriver',
            launchFile,
            'filename:='+self.filename,
            'runname:='+self.runName,
            'videodevice:='+videoDevice,
            'markersize:='+str(markerSize),
            'usbcamrosbag:='+self.usbCamBagFilename,
            'usbcamtopic:='+USBCAMERATOPIC,
            ];
        logging.debug('The Processing String for AR Listener: '+str(self.processString))

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
        time.sleep(1)
        importARData(self.filename,self.runName)
        importBagData(self.filename,self.usbCamBagFilename,self.runName)
        if os.path.isfile(self.usbCamBagFilename):
            os.remove(self.usbCamBagFilename)
        if os.path.isdir(self.tmpdir):
            os.rmdir(self.tmpdir)
        