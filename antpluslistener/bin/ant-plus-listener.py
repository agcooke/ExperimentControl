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
import sys
import time

from ant.core import driver
from ant.core import event
from ant.core.constants import RESPONSE_NO_ERROR
from ant.core.message import ChannelAssignMessage
from ant.core.message import ChannelFrequencyMessage
from ant.core.message import ChannelIDMessage
from ant.core.message import ChannelOpenMessage
from ant.core.message import ChannelPeriodMessage
from ant.core.message import ChannelSearchTimeoutMessage
from ant.core.message import NetworkKeyMessage
from ant.core.message import SystemResetMessage
from antpluslistener.core.SofieHdfFormatLogWriter import LogWriter
from antpluslistener.core.antlogging import setLogger
# USB1 ANT stick interface. Running `dmesg | tail -n 25` after plugging the
# stick on a USB port should tell you the exact interface.
SERIAL = '/dev/ttyUSB0'
NETKEY = '\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'
# ========== DO NOT CHANGE ANYTHING BELOW THIS LINE ==========
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
    #Setup the logger:
    theLogger = LogWriter(filename=options.outfile,runName=options.runname)
        
    # Initialize driver
    stick = driver.USB1Driver(SERIAL, log=theLogger,
        debug=DEBUG,baud_rate=4800)
    stick.open()

    # Initialize event machine
    evm = event.EventMachine(stick)
    evm.registerCallback(MyCallback())
    evm.start()

    # Reset
    print "\n\n-------------------------------\n:"
    print "Setting UP"
    print "\n\n-------------------------------\n"
    msg = SystemResetMessage()
    stick.write(msg.encode())
    time.sleep(1)

    # Set network key
    msg = NetworkKeyMessage(key=NETKEY)
    stick.write(msg.encode())
    if evm.waitForAck(msg) != RESPONSE_NO_ERROR:
        print 'ERROR SETTING UP: SETTING NETWORK KEY'
        sys.exit()

    # Initialize it as a receiving channel using our network key
    msg = ChannelAssignMessage()
    stick.write(msg.encode())
    if evm.waitForAck(msg) != RESPONSE_NO_ERROR:
        print 'ERROR SETTING UP: INITIALISING AS RECEIVING CHANNEL'
        sys.exit()

    # Now set the channel id for pairing with an ANT+ bike cadence/speed sensor
    msg = ChannelIDMessage(device_type=121)
    stick.write(msg.encode())
    if evm.waitForAck(msg) != RESPONSE_NO_ERROR:
        print 'ERROR SETTING UP: SETTING CHANNEL ID '
        sys.exit()

    # Listen forever and ever (not really, but for a long time)
    msg = ChannelSearchTimeoutMessage(timeout=255)
    stick.write(msg.encode())
    if evm.waitForAck(msg) != RESPONSE_NO_ERROR:
        print 'ERROR SETTING UPL LISTENING TIMEOUT'
        sys.exit()

    # We want a ~4.05 Hz transmission period
    msg = ChannelPeriodMessage(period=8085)
    stick.write(msg.encode())
    if evm.waitForAck(msg) != RESPONSE_NO_ERROR:
        print 'ERROR SETTING UP: TRANSMISSION FREQUENCY'
        sys.exit()

    # And ANT frequency 57, of course
    msg = ChannelFrequencyMessage(frequency=57)
    stick.write(msg.encode())
    if evm.waitForAck(msg) != RESPONSE_NO_ERROR:
        print 'ERROR SETTING UP: SETTING FREQUENCY'
        sys.exit()

    # Time to go live
    msg = ChannelOpenMessage()
    stick.write(msg.encode())
    if evm.waitForAck(msg) != RESPONSE_NO_ERROR:
        print 'ERROR SETTING UP: GOING LIVE'
        sys.exit()
        
    print "\n\n-------------------------------\n:"
    print "Listening for ANT events: Press CTRL+C to Exit."
    print "\n\n-------------------------------\n"
    try:
        while 1:
            time.sleep(100)
    except KeyboardInterrupt:
        pass;
    print "\n\n-------------------------------\nShutting down:"
    print "\n\n-------------------------------\n"
    msg = SystemResetMessage()
    stick.write(msg.encode())
    time.sleep(1)
    evm.stop()
    stick.close()
    print "\n\n-------------------------------\n:"
    print "EXITING"
    print "\n\n-------------------------------\n"