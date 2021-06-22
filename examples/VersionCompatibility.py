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
