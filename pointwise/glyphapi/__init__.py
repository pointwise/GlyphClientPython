#! /usr/bin/env python

#
# Copyright 2018 (c) Pointwise, Inc.
# All rights reserved.
#
# This sample Python script is not supported by Pointwise, Inc.
# It is provided freely for demonstration purposes only.
# SEE THE WARRANTY DISCLAIMER AT THE BOTTOM OF THIS FILE.
#

"""
This module provides a Python-like interface to Glyph.

GlyphAPI provides the service of automatically converting Python commands
that look like static method calls into Glyph static actions.
"""
from pointwise import GlyphClient
from pointwise import GlyphError

from .glyphobj import GlyphObj, GlyphVar
from .utilities import *

class GlyphAPI(object):
    """ This class provides access to Glyph static actions.  """

    def __init__(self, glyph_client):
        """ Initialize a GlyphAPI object from a connected GlyphClient.
        """
        self.glf = glyph_client
 
        # Acquire the list of all valid Glyph class names to seed the
        # name list
        if self.glf is not None and self.glf.is_connected():
            self._names = self.glf.eval(
                    'pw::Application getAllCommandNames')
        else:
            self._names = []
            raise GlyphError('', 'Not connected')

    def __getattr__(self, name):
        """ Create a GlyphObj object as needed for a Glyph class to invoke
            its static actions.
        """
        glfFunction = 'pw::' + name
        glfObj = None

        if glfFunction in self._names:
            glfObj = GlyphObj(glfFunction, self.glf)
            setattr(self, name, glfObj)

        return glfObj

#
# DISCLAIMER:
# TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, POINTWISE DISCLAIMS
# ALL WARRANTIES, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED
# TO, IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE, WITH REGARD TO THIS SCRIPT.  TO THE MAXIMUM EXTENT PERMITTED 
# BY APPLICABLE LAW, IN NO EVENT SHALL POINTWISE BE LIABLE TO ANY PARTY 
# FOR ANY SPECIAL, INCIDENTAL, INDIRECT, OR CONSEQUENTIAL DAMAGES 
# WHATSOEVER (INCLUDING, WITHOUT LIMITATION, DAMAGES FOR LOSS OF 
# BUSINESS INFORMATION, OR ANY OTHER PECUNIARY LOSS) ARISING OUT OF THE 
# USE OF OR INABILITY TO USE THIS SCRIPT EVEN IF POINTWISE HAS BEEN 
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGES AND REGARDLESS OF THE 
# FAULT OR NEGLIGENCE OF POINTWISE.
#
