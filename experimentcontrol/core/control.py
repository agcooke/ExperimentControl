'''
Contains the main logic for starting and stopping experiments.

Created on 13 Dec 2012

@author: cooke
'''
import logging
from sofiehdfformat.core.SofiePyTableAccess import SofiePyTableAccess
from experimentcontrol.core.ARListener import ARListener,BIGMARKER,SMALLMARKER
from experimentcontrol.core.AntPlusListener import AntPlusListener
from experimentcontrol.core.InertiaTechnologyListener import IntertiaTechnologyListener
from experimentcontrol.core.antlogging import setLogger
from experimentcontrol.core.InertiaTechnologyListener import IMUPORT,IMUHOST
from experimentcontrol.core.Exceptions import OutFileMustBeAbsolutePath,OutFileMustBeh5Extention
import os

ARHIGHTRES=True
def isCorrectFilename(filename):
    extensionOut = os.path.splitext(filename)
    if(extensionOut[1]!='.h5'):
        logging.debug( "\n\n-------------------------------\n")
        logging.debug("The Outfile ({0}) must be specified have an '.h5' extension.".\
            format(filename))
        logging.debug("\n\n-------------------------------\n")
        raise OutFileMustBeh5Extention
    if not os.path.isabs(filename):
        raise OutFileMustBeAbsolutePath

def startExperiment(outfile,runName,serialIMU,serialAnt,serialAR,
                    imuPort=IMUPORT,imuHost=IMUHOST,arHighRes=ARHIGHTRES,arMarkerSize=SMALLMARKER):
    logging.debug('Creating InertiaTechnoogyListener:')
    #tests
    if not os.path.isabs(outfile):
        raise OutFileMustBeAbsolutePath
    listeners = []
    if serialIMU:
        logging.debug("\n\n-------------------------------\n")
        logging.debug( "IMU ENABLED")
        logging.debug( "\n\n-------------------------------\n")
        inertiaTechnologyListener = IntertiaTechnologyListener(
            outfile,runName,serialIMU,
            port=imuPort,host=imuHost)
        inertiaTechnologyListener.open()
        listeners.append(inertiaTechnologyListener)

    if serialAnt:
        logging.debug( "\n\n-------------------------------\n")
        logging.debug( "ANT ENABLED")
        logging.debug( "\n\n-------------------------------\n")
        antPlusListener = AntPlusListener(outfile,
            runName,
            serialAnt)
        antPlusListener.open()
        listeners.append(antPlusListener)
    if serialAR:
        logging.debug( "\n\n-------------------------------\n")
        logging.debug( "AR ENABLED")
        logging.debug( "\n\n-------------------------------\n")
        arListener = ARListener(
            outfile,runName,
            serialAR,highRes=arHighRes,
            markerSize=arMarkerSize)
        arListener.open()
        listeners.append(arListener)
    return listeners

def syncListeners(listeners):
    for listener in listeners:
        listener.sync()

def shutDownExperiment(listeners):
    for listener in listeners:
        listener.close()