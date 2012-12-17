__author__="cooke"
__date__ ="$23-Nov-2011 17:16:55$"
from setuptools import setup, find_packages
import os
if os.name == 'nt':
    import py2exe
    
setup (
  name = 'ExperimentControl',
  version = '0.4',
  packages = find_packages(),
  install_requires=['sofiehdfformat','PythonCard','wxAnyThread'],
  author = 'ExperimentControl Team',
  author_email = 'adrian "dot" cooke {at} u t wente <dot> nl',
  description = 'USB Ant plust listener, IMU listerner and experiment run organiser.',
  url = 'https://github.com/agcooke/ExperimentControl',
  license = open('LICENSE.md').read(),
  long_description=open('README.md').read(),
  scripts = [os.path.join('experimentcontrol','bin','experiment-control.py'),
             os.path.join('experimentcontrol','bin','gui','experiment-control-gui.py')
             ],
  console = [os.path.join('experimentcontrol','bin','experiment-control.py')]
)
