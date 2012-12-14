#!/usr/bin/python
__author__="cooke"
__date__ ="$02-Feb-2012 15:26:23$"

"""
Initialize a basic broadcast slave channel for listening to
an ANT+ Bicycle cadence and speed senser, using raw messages
and event handlers.

"""
import logging
import optparse
from time import sleep
import os.path
from ant.core import event
from sofiehdfformat.core.SofiePyTableAccess import SofiePyTableAccess
from experimentcontrol.core.ARListener import ARListener,BIGMARKER,SMALLMARKER
from experimentcontrol.core.AntPlusListener import AntPlusListener
from experimentcontrol.core.InertiaTechnologyListener import IntertiaTechnologyListener
from experimentcontrol.core.antlogging import setLogger
from experimentcontrol.core.control import startExperiment, syncListeners,shutDownExperiment,isCorrectFilename
from experimentcontrol.core.Exceptions import OutFileMustBeAbsolutePath, OutFileMustBeh5Extention
NETKEY = '\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'

# Event callback
class MyCallback(event.EventCallback):
    def process(self, msg):
        pass

if __name__ == '__main__':
    usage = """usage: %prog [options] arg1
This package is used log data from the sparkfun usb stick
    """
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--outfile', '-o', default=None,
        help="The HDF file where the data will be saved (You must specify an"+\
        ' absolute path).')
    parser.add_option('--verbose', '-v', action="store_true", dest="verbose",
        default=False,help="Enable verbose mode.")
    parser.add_option('--runname', '-t', default=None,
        help="The Run that you are doing.")
    parser.add_option('--serialant', '-s', default=None,
        help="Serial Device of the ANT Stick.")
    parser.add_option('--serialimu', '-i', default=None,
        help="Serial Device of the IMU's.")
    parser.add_option('--imuport', '-p', default=1234,
        help="The Port for the IMU socket server, defaults to 1234.")
    parser.add_option('--imuhost', '-m', default='127.0.0.1',
        help="The host for the IMU socket server.")
    parser.add_option('--serialar', '-a', default=None,
        help="The camera to use for the ROS AR tracking.")
    parser.add_option('--highres', '-c', action="store_true", dest="highres",
        default=False,help="Defaults to low res.")
    parser.add_option('--bigmarker', '-n', dest="bigmarker",
        action="store_const",
        const=BIGMARKER,
        default=SMALLMARKER,
        help="Defaults to small marker.")
    options, arguments = parser.parse_args()
    if options.verbose:
        setLogger(logging.DEBUG)
        print "\n\n-------------------------------\n"
        print "VERBOSE MODE."
        print "\n\n-------------------------------\n"
        logging.debug('Enabled DEBUG MODE')
        DEBUG=True
    if(options.outfile==None):
        print "\n\n-------------------------------\n"
        print "Specify the out file (--outfile filename)"
        print "\n\n-------------------------------\n"
        exit()
    try:
        isCorrectFilename(options.outfile);
    except OutFileMustBeh5Extention:
        print "\n\n-------------------------------\n"
        print "The Outfile ({0}) must be specified have an '.h5' extension.".\
            format(options.outfile)
        print "\n\n-------------------------------\n"
        exit()
    except OutFileMustBeAbsolutePath:
        print "\n\n-------------------------------\n"
        print "The Outfile ({0}) must be specified as an absolute path.".\
            format(options.outfile)
        print "\n\n-------------------------------\n"
        exit()

    if(options.runname==None):
        print "\n\n-------------------------------\n"
        print "Specify the rest run name (--runname 01CornerTestRun) "
        print "\n\n-------------------------------\n"
        exit()
    currentRuns = SofiePyTableAccess.getRunsInTheFile(options.outfile,
        options.runname)
    if currentRuns:
        print "\n\n-------------------------------\n"
        print "The run '{0}' is already in the file '{1}':\n\nCurrent Runs:\n{2}".\
            format(options.runname,options.outfile,currentRuns)
        print "\n\n-------------------------------\n"
        exit()
    
    listeners = \
        startExperiment(options.outfile, options.runname,
                    options.serialimu,options.serialant,options.serialar,
                    imuPort=options.imuport,imuHost=options.imuhost,
                    arHighRes=options.highres,arMarkerSize=options.bigmarker)
   
    print "\n\n-------------------------------\n"
    print "LOGGING SETUP: CALLIBRATION STILL PERIOD STARTS"
    print "\n\n-------------------------------\n"
    i=8;
    weBeenInterrupted = False
    try:
        while i>0:
            sleep(1)
            i -= 1
            print '.'
    except KeyboardInterrupt:
        weBeenInterrupted = True; 
    print "\n\n-------------------------------\n"
    print "YOU CAN NOW START THE  EXPERIMENT"
    print "\n\n-------------------------------\n"
    
    try:
        while weBeenInterrupted==False:

            command=raw_input('HIT ENTER TO SEND SYNC SIGNALS:')
            logging.debug("raw_input = {0}".format(command));
            syncListeners(listeners)
            print 'SYNC SIGNAL SENT'
    except KeyboardInterrupt:
        pass;
    print "\n\n-------------------------------\n"
    print "EXPERIMENT STOPPED: STILL PERIOD AT END STARTING"
    print "\n\n-------------------------------\n"
    i=5;
    try:
        while i>0:
            sleep(1)
            i -= 1
            print '.'
    except KeyboardInterrupt:
        print 'END STILL PERIOD INTERRUPTED'
    print "\n\n-------------------------------------------------------"
    print "-------------------------------------------------------"
    print "-------------------------------------------------------"
    print "SHUTTING DOWN"
    print "\n\n-------------------------------\n"
    shutDownExperiment(listeners)
    print "EXITING (YOU CAN NOW MOVE): RUN {0}  in file {1} COMPLETED".format(
        options.runname,options.outfile)
    print "\n\n-------------------------------\n"