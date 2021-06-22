#! /usr/bin/env python

#############################################################################
#
# (C) 2021 Cadence Design Systems, Inc. All rights reserved worldwide.
#
# This sample script is not supported by Cadence Design Systems, Inc.
# It is provided freely for demonstration purposes only.
# SEE THE WARRANTY DISCLAIMER AT THE BOTTOM OF THIS FILE.
#
#############################################################################

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

#############################################################################
#
# This file is licensed under the Cadence Public License Version 1.0 (the
# "License"), a copy of which is found in the included file named "LICENSE",
# and is distributed "AS IS." TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE
# LAW, CADENCE DISCLAIMS ALL WARRANTIES AND IN NO EVENT SHALL BE LIABLE TO
# ANY PARTY FOR ANY DAMAGES ARISING OUT OF OR RELATING TO USE OF THIS FILE.
# Please see the License for the full text of applicable terms.
#
#############################################################################
