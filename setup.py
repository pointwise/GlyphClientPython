#! /usr/bin/env python

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pointwise-glyph-client',
      version='2.0.0',
      description='Glyph client in Python with Python-like API to Pointwise Glyph Server',
      url='http://github.com/pointwise/GlyphClientPython',
      install_requires=['numpy'],
      packages=['pointwise', 'pointwise.glyphapi'])
