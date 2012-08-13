#!/usr/bin/python
__author__="cooke"
__date__ ="$02-Feb-2012 15:26:23$"

"""
Initialize a basic broadcast slave channel for listening to
an ANT+ Bicycle cadence and speed senser, using raw messages
and event handlers.

"""
from ant.core import event
import logging
import optparse
from time import sleep

from experimentcontrol.core.ARListener import ARListener
from experimentcontrol.core.AntPlusListener import AntPlusListener
from experimentcontrol.core.InertiaTechnologyListener import IntertiaTechnologyListener
from experimentcontrol.core.antlogging import setLogger
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
        help="The HDF file where the data will be saved.")
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
    parser.add_option('--imuhost', '-m', default='localhost',
        help="The host for the IMU socket server.")
    parser.add_option('--ardevice', '-a', default=None,
        help="The camera to use for the ROS AR tracking.")
    options, arguments = parser.parse_args()
    if options.verbose:
        setLogger(logging.DEBUG)
        print "VERBOSE MODE."
        logging.debug('Enabled DEBUG MODE')
        DEBUG=True
    if(options.outfile==None):
        print "Specify the out file (--outfile filename)"
        exit()
    if(options.runname==None):
        print "Specify the rest run name (--runname 01CornerTestRun) "
        exit()

    logging.debug('Creating InertiaTechnoogyListener:')
    if options.serialimu:
        print "\n\n-------------------------------\n:"
        print "IMU ENABLED"
        print "\n\n-------------------------------\n"
        intertiaTechnologyListener = IntertiaTechnologyListener(
            options.outfile,options.runname,
            options.imuport,options.imuhost,options.serialimu)
        intertiaTechnologyListener.open()
        
    if options.ardevice:
        print "\n\n-------------------------------\n:"
        print "AR ENABLED"
        print "\n\n-------------------------------\n"
        arListener = ARListener(
            options.outfile,options.runname,
            options.ardevice)
        arListener.open()

    if options.serialant:
        print "\n\n-------------------------------\n:"
        print "ANT ENABLED"
        print "\n\n-------------------------------\n"
        antPlusListener = AntPlusListener(options.outfile,
            options.runname,
            options.serialant)
        antPlusListener.open()
    print "\n\n-------------------------------\n:"
    print "LOGGING SETUP: CALLIBRATION STILL PERIOD STARTS"
    print "\n\n-------------------------------\n"
    i=8;
    while i>0:
        sleep(1)
        i -= 1
        print '.'
    print "\n\n-------------------------------\n:"
    print "YOU CAN NOW START THE  EXPERIMENT"
    print "\n\n-------------------------------\n"
    try:
        while 1:

            command=raw_input('HIT ENTER TO SEND SYNC SIGNALS:')
            logging.debug("raw_input = {0}".format(command));
            #1=Trigger event for syncing.
            logging.debug('SYNC')
            if options.serialimu:
                print "IMU SYNC"
                intertiaTechnologyListener.sync()
            if options.serialant:
                print "ANT SYNC"
                antPlusListener.sync()
    except KeyboardInterrupt:
        pass;
    print "\n\n-------------------------------\n:"
    print "EXPERIMENT STOPPED: STILL PERIOD AT END STARTING"
    print "\n\n-------------------------------\n"
    sleep(5)
    print "\n\n-------------------------------\n:"
    print "SHUTTING DOWN"
    print "\n\n-------------------------------\n"
    if options.serialant:
        print "CLOSING ANT"
        antPlusListener.close()
    if options.serialimu:
        print "CLOSING IMU"
        intertiaTechnologyListener.close()
    if options.ardevice:
        print "CLOSING AR"
        arListener.close()
    print "\n\n-------------------------------\n:"
    print "EXITING (YOU CAN NOW MOVE):"+options.runname+' completed.'
    print "\n\n-------------------------------\n"