#############################################################################
#
# (C) 2021 Cadence Design Systems, Inc. All rights reserved worldwide.
#
# This sample script is not supported by Cadence Design Systems, Inc.
# It is provided freely for demonstration purposes only.
# SEE THE WARRANTY DISCLAIMER AT THE BOTTOM OF THIS FILE.
#
#############################################################################

""" This is an example script that creates a Glyph Server process,
    connects to it, and prints a Glyph message that is captured
    and printed to the console window.
"""

from pointwise import GlyphClient
from pointwise.glyphapi import *

# Callback function for output from Glyph Server
def echo(line):
    print("Script: {0}".format(line), end='')  # Not Python 2.7 compatible

# Port 0 indicates a non-interactive server process should be created
# in the background (consumes a Pointwise license).
with GlyphClient(port=0, callback=echo) as glf:

    # Use the Glyph API for Python
    pw = glf.get_glyphapi()

    glf.puts("Hello from '%s'" % pw.Application.getVersion())

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
