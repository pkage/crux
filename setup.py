#!/usr/bin/env python

import os
from setuptools import setup

# quick hack to recursively find all web files
def package_files(directory, remove):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join(path, filename).replace(remove, '', 1))
    return paths

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
          'crux.wizards.web': package_files('crux/wizards/web/static/', 'crux/wizards/web/')
      },
      include_package_data=True
     )
