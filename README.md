===========================================================================

Introduction to Experiment Control:
============
Python package that is used to manage sensors and experiment process within the (SOFIE project)[http://mobilitylabtwente.nl/sofie]

Contact
-------
Contact via:
    adrian "dot" cooke {at} u t wente 'dot' nl with all the correct symbols
replaced and whitespace removed.

Documentation
-------------
The code will be the documentation.

Description on how to start an experiment:
- Connect the IMU, speed sensor and camera with the laptop, using usb.
- Check in the terminal the name of the device (to see serial devices: ls /dev/tty*):
        - 2 serial devices: /dev/tty/USB0 /dev/tty/USB1 (they are named in order of connection)
        - 1 video device: /dev/video0
- To start up the measurements of the IMU's, initially some settings has to be changed:
    - menu < File < Capture: set the serial port to the usb where you connected the IMU and press start - close the window
    - menu < Options < Configuration < Wireless, set no of nodes to 13. Click 'Gateway', click 'Set' and 'yes'
    - now the IMU's start measuring.
- To start up an experiment:
    - Open the sofie environment:  type: work on sofie (in terminal)
    - experiment-control.py -h (gives help on the inputs to start up the python script 'experiment control'
    - -o name of output file (absolute, with path)
    - define devices: -s (serial ant = speed sensor) /dev/ttyUSB0 (or 1..) -i (IMU), -a (AR, video), -t (runname).
    - then everything starts up
    - to stop, press ctrl C
    - to see the output open up the .h5 file in vitables


Dependencies
------------
PythonCard -  Install from repository.
PyTables - Best way to get this set up is to just install vitables from the repository.
Install
===========
Linux:
-------
Clone from git hub or download a latest tag.

Install if you would like to:
% python setup.py install

Windows will not be supported at this stage.
