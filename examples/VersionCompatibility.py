#
# Copyright 2019 (c) Pointwise, Inc.
# All rights reserved.
#
# This sample Python script is not supported by Pointwise, Inc.
# It is provided freely for demonstration purposes only.
# SEE THE WARRANTY DISCLAIMER AT THE BOTTOM OF THIS FILE.
#

""" This is an example script that creates a Glyph Server process,
    connects to it with version compatability set, and prints some
    version-specific information to the console window.
"""

# About Glyph Version Compatability:
#
#   When running Pointwise versions prior to V18.3, the Glyph version
#   compatability level will always be the implemented Glyph version.  When
#   running V18.3 or later, a compatability version may be requested.
#   Compatability levels are used to modify certain default behaviors, e.g.,
#   meshing parameters, and correspond directly to a Glyph package version.

from pointwise import GlyphClient
from pointwise.glyphapi import *

DomDefaults = {
        "TRexGrowthRate",
        "TRexSpacingSmoothing" }

BlkDefaults = {
        "TRexGrowthRate",
        "TRexCollisionBuffer",
        "TRexSkewCriteriaMaximumAngle" }

def printDefaults(pw, v):
    print("Pointwise Version               : %s" % pw.Application.getVersion())
    print("Glyph Compatability Version     : %s" % pw.glf._version)
    print("DomainUnstructured:")
    for d in DomDefaults:
        print("  %-30.30s: %s" % (d, pw.DomainUnstructured.getDefault(d)))
    print("BlockUnstructured:")
    for b in BlkDefaults:
        print("  %-30.30s: %s" % (b, pw.BlockUnstructured.getDefault(b)))
    print("-----")


# Port 0 indicates a non-interactive server process should be created in the
# background (consumes a Pointwise license).

# 'tclsh' must be in your PATH and, for non-Windows platforms, all other
# environment variables needed to load the Glyph package must be set
# accordingly.

# No version compatability
with GlyphClient(port=0) as glf:

    pw = glf.get_glyphapi()
    printDefaults(pw, "None")

# V18.0 compatability
with GlyphClient(port=0, version="2.18.0") as glf:

    pw = glf.get_glyphapi()
    printDefaults(pw, "2.18.0")

# V18.2 compatability
with GlyphClient(port=0, version="2.18.2") as glf:

    pw = glf.get_glyphapi()
    printDefaults(pw, "2.18.2")

# V18.3 compatability
with GlyphClient(port=0, version="3.18.3") as glf:

    pw = glf.get_glyphapi()
    printDefaults(pw, "3.18.3")

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
