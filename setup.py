#! /usr/bin/env python

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pointwise-glyph-client',
      version='1.0',
      description='Python client to Pointwise Glyph Server',
      url='http://github.com/pointwise/GlyphClientPython')