#!/usr/bin/env python

from setuptools import setup

setup(name='crux',
      version='0.0.1',
      description='flexible data pipeline',
      author='Patrick Kage',
      author_email='pkage@mit.edu',
      packages=['crux', 'crux.client', 'crux.backend', 'crux.common'],
      install_requires=['pyzmq', 'msgpack-python', 'jsonschema', 'termcolor'],
      entry_points={
          'console_scripts': []
      }
     )
