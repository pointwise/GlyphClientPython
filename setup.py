#! /usr/bin/env python

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pointwise-glyph-client',
      version='2.0.13',
      description='Glyph client in Python with Python-like API to Pointwise Glyph Server',
      url='http://github.com/pointwise/GlyphClientPython',
      install_requires=['numpy'],
      packages=['pointwise', 'pointwise.glyphapi'],
      classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 2.7'],
      author='Cadence Design Systems, Inc.',
      author_email='pw-pypi@cadence.com')
