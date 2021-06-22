#############################################################################
#
# (C) 2021 Cadence Design Systems, Inc. All rights reserved worldwide.
#
# This sample script is not supported by Cadence Design Systems, Inc.
# It is provided freely for demonstration purposes only.
# SEE THE WARRANTY DISCLAIMER AT THE BOTTOM OF THIS FILE.
#
#############################################################################

""" This is an example script that prints information about domains.
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
  # Select domains only, of any type
  sm = pw.Display.createSelectionMask(requireDomain=[])
  # Grab the current selection
  pw.Display.getSelectedEntities(selection, selectionmask=sm)
  
  doms = selection["Domains"]
  
  # If no domains were selected already, ask the user to select some
  if len(doms) == 0 and pw.Display.selectEntities(selection, selectionmask=sm, \
      description="Select domains to display segment information"):
    doms = selection["Domains"]

  if (len(doms) > 0):
    # For each selected domain...
    for dom in doms:
      glf.puts("Domain %s" % dom.getName())
      # For each edge in the domain...
      for e in range(1, dom.getEdgeCount()+1):
        glf.puts("  Edge %d" % e)
        # For each connector in the edge...
        edge = dom.getEdge(e)
        for k in range(1, edge.getConnectorCount()+1):
          con = edge.getConnector(k)
          glf.puts("    Connector %d: %s %s" % (k, con.getName(), edge.getConnectorDirection(k)))

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
