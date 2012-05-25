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
from experimentcontrol.core.SofieHdfFormatLogWriter import LogWriter
from experimentcontrol.core.antlogging import setLogger
NETKEY = '\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'

# Event callback
class MyCallback(event.EventCallback):
    def process(self, msg):
        pass

class AntPlusListener(object):
    """
    Used to start and stop the ant plus listener
    """
    def __init__(self,outfile,runName,serial):
        self.outfile = outfile;
        self.runName = runName;
        self.serial = serial;
        self.logger = None;


    def open(self):
        #Setup the logger:
        self.logger = LogWriter(filename=self.outfile,runName=self.runName)
        # Initialize driver
        self.stick = driver.USB1Driver(self.serial, log=self.logger,debug=True,
            baud_rate=4800)
        self.stick.open()

        # Initialize event machine
        self.evm = event.EventMachine(self.stick)
        self.evm.registerCallback(MyCallback())
        self.evm.start()

        # Reset
        logging.debug( "\n\n-------------------------------\n:")
        logging.debug( "Setting UP")
        logging.debug( "\n\n-------------------------------\n")
        msg = SystemResetMessage()
        self.stick.write(msg.encode())
        time.sleep(1)

        # Set network key
        msg = NetworkKeyMessage(key=NETKEY)
        self.stick.write(msg.encode())
        if self.evm.waitForAck(msg) != RESPONSE_NO_ERROR:
            logging.debug( 'ERROR SETTING UP: SETTING NETWORK KEY')
            sys.exit()

        # Initialize it as a receiving channel using our network key
        msg = ChannelAssignMessage()
        self.stick.write(msg.encode())
        if self.evm.waitForAck(msg) != RESPONSE_NO_ERROR:
            logging.debug( 'ERROR SETTING UP: INITIALISING AS RECEIVING CHANNEL')
            sys.exit()

        # Now set the channel id for pairing with an ANT+ bike cadence/speed sensor
        msg = ChannelIDMessage(device_type=121)
        self.stick.write(msg.encode())
        if self.evm.waitForAck(msg) != RESPONSE_NO_ERROR:
            logging.debug( 'ERROR SETTING UP: SETTING CHANNEL ID ')
            sys.exit()

        # Listen forever and ever (not really, but for a long time)
        msg = ChannelSearchTimeoutMessage(timeout=255)
        self.stick.write(msg.encode())
        if self.evm.waitForAck(msg) != RESPONSE_NO_ERROR:
            logging.debug( 'ERROR SETTING UPL LISTENING TIMEOUT')
            sys.exit()

        # We want a ~4.05 Hz transmission period
        msg = ChannelPeriodMessage(period=8085)
        self.stick.write(msg.encode())
        if self.evm.waitForAck(msg) != RESPONSE_NO_ERROR:
            logging.debug( 'ERROR SETTING UP: TRANSMISSION FREQUENCY')
            sys.exit()

        # And ANT frequency 57, of course
        msg = ChannelFrequencyMessage(frequency=57)
        self.stick.write(msg.encode())
        if self.evm.waitForAck(msg) != RESPONSE_NO_ERROR:
            logging.debug( 'ERROR SETTING UP: SETTING FREQUENCY')
            sys.exit()

        # Time to go live
        msg = ChannelOpenMessage()
        self.stick.write(msg.encode())
        if self.evm.waitForAck(msg) != RESPONSE_NO_ERROR:
            logging.debug( 'ERROR SETTING UP: GOING LIVE')
            sys.exit()

        logging.debug( "\n\n-------------------------------\n:")
        logging.debug( "Listening for ANT events: Press CTRL+C to Exit.")
        logging.debug( "\n\n-------------------------------\n")

    def close(self):
        logging.debug( "\n\n-------------------------------\nShutting down:")
        logging.debug( "\n\n-------------------------------\n")
        msg = SystemResetMessage()
        self.stick.write(msg.encode())
        time.sleep(1)
        self.evm.stop()
        self.stick.close()
    def sync(self):
        print 'ANT SYNCING'
        self.logger.sync()