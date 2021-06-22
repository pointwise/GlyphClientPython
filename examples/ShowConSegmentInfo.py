#############################################################################
#
# (C) 2021 Cadence Design Systems, Inc. All rights reserved worldwide.
#
# This sample script is not supported by Cadence Design Systems, Inc.
# It is provided freely for demonstration purposes only.
# SEE THE WARRANTY DISCLAIMER AT THE BOTTOM OF THIS FILE.
#
#############################################################################

""" This is an example script that prints information about each
    curve segment of a connector.
"""

from pointwise import GlyphClient
from pointwise.glyphapi import *

# Connect to Glyph Server (Pointwise) on the default port
with GlyphClient() as glf:
  pw = glf.get_glyphapi()

  # Since selection is required, this script can only be run in interactive mode
  if not pw.Application.isInteractive():
    raise Exception("This script can only be run in interactive mode")

  # Create a Tcl variable to capture the selection results
  selection = GlyphVar()
  # Select connectors only, of any type
  sm = pw.Display.createSelectionMask(requireConnector=[])
  # Grab the current selection
  pw.Display.getSelectedEntities(selection, selectionmask=sm)
  
  cons = selection["Connectors"]
  
  # If no connectors were selected already, ask the user to select some
  if len(cons) == 0 and pw.Display.selectEntities(selection, selectionmask=sm, \
      description="Select connectors to display segment information"):
    cons = selection["Connectors"]

  if (len(cons) > 0):
    # For each selected connector...
    for con in cons:
      # Print the name of the connector to the message window
      glf.puts("Connector %s" % con.getName())
      # For each segment of that connector...
      for n in range(1, con.getSegmentCount()+1):
        glf.puts("  Segment %d" % n)
        segment = con.getSegment(n)
        for k in range(1, segment.getPointCount()+1):
          xyz = Vector3(segment.getXYZ(control=k))
          glf.puts("    Point %3d: %15.8f %15.8f %15.8f" % (k, xyz.x, xyz.y, xyz.z))

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
