from subprocess import Popen
import logging
import time
import roslib; roslib.load_manifest('sofiehdfformat_rosdriver')
from sofiehdfformat_rosdriver.fileUtils import importARData,importBagData
from sofiehdfformat.core.config import getDefaultBagFileName,getARSubDirectory,getDefaultCSVFileName
from sofiehdfformat.core.SofieFileUtils import cleanUpTempDirectory,createTempAndFileDirectory
import os, tempfile
SMALLMARKER=58.7
BIGMARKER=97.0
USBCAMERATOPIC='/usb_cam/image_raw'

class ARListener(object):
    """
    Used to start and stop the ant plus listener
    """
    def __init__(self,outfile,runName,videoDevice,highRes=False,markerSize=SMALLMARKER):
        if highRes == False:
            launchFile = 'simple_bridge_normal.launch'
        else:
            launchFile = 'simple_bridge_1920.launch'
        self.hdfFilename = outfile
        self.temporyCSVFilename = createTempAndFileDirectory(getDefaultCSVFileName())
        self.temporaryUSBCamBagFilename = createTempAndFileDirectory(getDefaultBagFileName())
        logging.debug('The CSV TMP FILE: {0}: The Bag File:{1}'.format(self.temporyCSVFilename,
                                                                       self.temporaryUSBCamBagFilename))
        self.runName = getARSubDirectory(runName)
        self.runNameBase = runName
        #THE STRING USED TO START UP THE roslaunch sofiehdfformat_rosdriver' ROS launch file
        self.processString = \
            ['roslaunch',
            'sofiehdfformat_rosdriver',
            launchFile,
            'csvfilename:='+self.temporyCSVFilename,
            'videodevice:='+videoDevice,
            'markersize:='+str(markerSize),
            'usbcamrosbag:='+self.temporaryUSBCamBagFilename,
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
        importARData(self.temporyCSVFilename,self.hdfFilename,self.runName)
        cleanUpTempDirectory(self.temporyCSVFilename)
        importBagData(self.temporaryUSBCamBagFilename,self.hdfFilename,self.runNameBase)
        cleanUpTempDirectory(self.temporaryUSBCamBagFilename)
        