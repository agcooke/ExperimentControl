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
import time

from ant.core import event
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
    parser.add_option('--serialant', '-s', default='/dev/ttyUSB0',
        help="Serial Device of the ANT Stick.")
    parser.add_option('--serialimu', '-i', default='/dev/ttyUSB1',
        help="Serial Device of the IMU's.")
    parser.add_option('--imuport', '-p', default=1234,
        help="The Port for the IMU socket server.")
    parser.add_option('--imuhost', '-m', default='localhost',
        help="The host for the IMU socket server.")
    options, arguments = parser.parse_args()
    if options.verbose:
        ch = setLogger(DEBUGLEVEL=logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger().addHandler(ch)
        logging.debug("TEST")
    DEBUG=True
    if(options.outfile==None):
        print "Specify the out file (--outfile filename)"
        exit()
    if(options.runname==None):
        print "Specify the rest run name (--runname 01CornerTestRun) "
        exit()

    #antPlusListener = AntPlusListener(options.outfile,
    #    options.runname,
    #    options.serialant)
    intertiaTechnologyListener = IntertiaTechnologyListener(
        options.outfile,options.runname,
        options.imuport,options.imuhost,options.serialimu)
    #antPlusListener.open()
    try:
        while 1:
            time.sleep(100)
    except KeyboardInterrupt:
        pass;
    intertiaTechnologyListener.close()
    #antPlusListener.close()
    print "\n\n-------------------------------\n:"
    print "EXITING"
    print "\n\n-------------------------------\n"