#############################################################################
#
# (C) 2021 Cadence Design Systems, Inc. All rights reserved worldwide.
#
# This sample script is not supported by Cadence Design Systems, Inc.
# It is provided freely for demonstration purposes only.
# SEE THE WARRANTY DISCLAIMER AT THE BOTTOM OF THIS FILE.
#
#############################################################################

""" This is an example script that prints the orientation of all
    the faces in a block, and the relative orientation of all the
    domains in each face.
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
  # Select blocks only, of any type
  sm = pw.Display.createSelectionMask(requireBlock=[])
  # Grab the current selection
  pw.Display.getSelectedEntities(selection, selectionmask=sm)
  
  blocks = selection["Blocks"]
  
  # If no blocks were selected already, ask the user to select some
  if len(blocks) == 0 and pw.Display.selectEntities(selection, selectionmask=sm, \
      description="Select blocks to display face/domain orientations"):
    blocks = selection["Blocks"]

  if (len(blocks) > 0):
    # For each selected block...
    for block in blocks:
      # Print the name of the block to the message window
      glf.puts("Block %s" % block.getName())
      # For each face of that block...
      for n in range(1, block.getFaceCount()+1):
        face = block.getFace(n)
        if face.isOfType("pw::FaceUnstructured"):
          # Print the face orientation (In or Out)
          glf.puts("  Face %d %s" % (n, face.getNormalOrientation()))
        else:
          glf.puts("  Face %d" % n)
        # for each domain in the face...
        for k in range(1, face.getDomainCount()+1):
          dom = face.getDomain(k)
          # Print the domain orientation (Same or Opposite), where "Same" means the domain
          # is oriented the same direction as the face)
          glf.puts("    Domain %s: %s" % (dom.getName(), face.getDomainOrientation(k)))

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
