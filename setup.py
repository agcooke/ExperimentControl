__author__="cooke"
__date__ ="$23-Nov-2011 17:16:55$"
from setuptools import setup, find_packages
import os
if os.name == 'nt':
    import py2exe    
setup (
  name = 'experimentcontrol',
  version = '0.5.0',
  packages = find_packages(),
  install_requires=['wxAnyThread','vitables'],
  author = 'ExperimentControl Team',
  author_email = 'adrian "dot" cooke {at} u t wente <dot> nl',
  description = 'USB Ant plust listener, IMU listerner and experiment run organiser.',
  url = 'https://github.com/agcooke/ExperimentControl',
  license = open('LICENSE.md').read(),
  long_description=open('README.md').read(),
  package_data = {
        # If any package contains *.txt files, include them:
        '': ['*.txt', 'data/*'],
    },
  scripts = [os.path.join('bin','experiment-control.py'),
             os.path.join('bin','gui','experiment-control-gui.py'),
             ],
  console = [os.path.join('bin','experiment-control.py')]
)
