from subprocess import Popen
import logging
import time
from sofiehdfformat.core.SofieFileUtils import importARData,importBagData
from sofiehdfformat.core.config import getDefaultBagFileName,getARSubDirectory,\
    getDefaultCSVFileName,getArduinoSubDirectory
from sofiehdfformat.core.SofieFileUtils import cleanUpTempDirectory,createTempAndFileDirectory
SMALLMARKER=12.0
BIGMARKER=10.0
USBCAMERATOPIC='/usb_cam/image_raw'

class ARListener(object):
    """
    Used to start and stop the Augemente Reality listener: The Ros project [sofie_ros](https://github.com/agcooke/sofie_ros)
    handles this.
    
    - The AR Tracker runs from here
    - Other arduino sensors will have to be added to this package.
    """
    def __init__(self,outfile,runName,arDevice,arduinoDevice,highRes=False,markerSize=SMALLMARKER,
                 recordVideo=False):
        launchFile = 'simple_bridge_normal.launch'
        self.hdfFilename = outfile
        self.temporyCSVFilename = createTempAndFileDirectory(getDefaultCSVFileName())
        self.temporaryUSBCamBagFilename = createTempAndFileDirectory(getDefaultBagFileName())
        logging.debug('The CSV TMP FILE: {0}: The Bag File:{1}'.format(self.temporyCSVFilename,
                                                                       self.temporaryUSBCamBagFilename))
        self.temporyCSVFilenameArduino = createTempAndFileDirectory(getDefaultCSVFileName())
        self.runNameArduino = getArduinoSubDirectory(runName)
        self.runName = getARSubDirectory(runName)
        self.runNameBase = runName
        #THE STRING USED TO START UP THE roslaunch sofiehdfformat_rosdriver' ROS launch file
        self.processString = \
            ['roslaunch',
            'sofie_ros',
            launchFile,
            'csvfilename:='+self.temporyCSVFilename,
            'videodeviceconnected:='+str(int(arDevice is not None)),
            'videodevice:='+str(arDevice),
            'arduinodeviceconnected:='+str(int(arduinoDevice is not None)),
            'arduinodevice:='+str(arduinoDevice),
            'arduinocsvfilename:='+self.temporyCSVFilenameArduino,
            'markersize:='+str(markerSize),
            'usbcamrosbag:='+self.temporaryUSBCamBagFilename,
            'usbcamtopic:='+USBCAMERATOPIC,
            'recordvideo:='+str(recordVideo).lower(),
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
        importARData(self.temporyCSVFilenameArduino,self.hdfFilename,self.runNameArduino)
        cleanUpTempDirectory(self.temporyCSVFilename)
        importBagData(self.temporaryUSBCamBagFilename,self.hdfFilename,self.runNameBase)
        cleanUpTempDirectory(self.temporaryUSBCamBagFilename)
        