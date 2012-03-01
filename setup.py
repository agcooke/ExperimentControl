__author__="cooke"
__date__ ="$23-Nov-2011 17:16:55$"
from setuptools import setup, find_packages
import os
if os.name == 'nt':
    import py2exe
setup (
  name = 'antplustlistener',
  version = '0.1',
  packages = find_packages(),
  install_requires=['sofiehdfformat'],
  author = 'AntPlusListener Team',
  author_email = 'adrian "dot" cooke {at} u t wente <dot> nl',
  description = 'USB Ant plust listener.',
  url = 'https://github.com/agcooke/antpluslistener',
  license = open('LICENSE.md').read(),
  long_description=open('README.md').read(),
  scripts = [os.path.join('antpluslistener','bin','ant-plus-listener.py')],
  console = [os.path.join('antpluslistener','bin','ant-plus-listener.py')]
)