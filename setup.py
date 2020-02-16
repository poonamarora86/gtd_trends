#!/usr/bin/env python

from setuptools import setup, find_packages
from codecs import open
from os import path
from distutils.core import setup

__version__ = '1.0.0'

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split("\n")

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]


setup(name='GTD_analysis',
      version='1.0',
      description='Dashboard of the analysis',
      author='Poonam Arora',
      author_email='aroracapri2004@gmail.com',
      url='https://github.com/poonamaarora86/Aleph',
      packages=find_packages(exclude=['docs', 'tests*']),
      include_package_data=True,
      dependency_links=dependency_links
     )
