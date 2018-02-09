#!/usr/bin/env python

from setuptools import setup

setup(name='crux',
      version='0.0.1',
      description='flexible data pipeline',
      author='Patrick Kage',
      author_email='pkage@mit.edu',
      packages=[
          'crux',
          'crux.client',
          'crux.backend',
          'crux.common',
          'crux.pipeline',
          'crux.wizards',
          'crux.wizards.web'
      ],
      install_requires=[
          'pyzmq',
          'msgpack-python',
          'jsonschema',
          'termcolor',
          'semver',
          'click',
          'progressbar2',
          'aiohttp',
          'aiodns',
          'cchardet'
      ],
      entry_points={
          'console_scripts': [
            'crux_daemon=crux.backend.launch:main',
            'crux=crux.wizards.launch:launch'
          ]
      },
      package_data={
          'crux.wizards.web': ['static/*']
      },
      include_package_data=True
     )
