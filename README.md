===========================================================================

Introduction to Experiment Control:
============
Python package that is used to manage sensors and experiment process within the (SOFIE project)[http://mobilitylabtwente.nl/sofie]

Contact
-------
Contact via:
    vera "dot" bulsink {at} u t wente 'dot' nl with all the correct symbols
replaced and whitespace removed.

Documentation
-------------
The console script is not used much anymore so might not work.

The gui in ./bin/gui/experiment-control-gui.py is the main entry to use the system.

Installation
===========
Linux:
-------
If you install from pip in ubuntu you need 'libhdf5-serial-dev' to get it to compile.
	$ sudo apt-get install libhdf5-serial-dev

Install if you would like to, download from GitHub
		% python setup.py install
		or simply from pip:
		% pip install -e git+git://github.com/agcooke/ExperimentControl.git#egg=experimentcontrol

Windows will not be supported at this stage.
