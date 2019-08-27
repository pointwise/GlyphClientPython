#
# Copyright 2018 (c) Pointwise, Inc.
# All rights reserved.
#
# This sample Python script is not supported by Pointwise, Inc.
# It is provided freely for demonstration purposes only.
# SEE THE WARRANTY DISCLAIMER AT THE BOTTOM OF THIS FILE.
#

from pointwise import GlyphClient
from pointwise.glyphapi import *
import copy

##########################################################
# Main Program

with GlyphClient() as glf:
    pw = glf.get_glyphapi()

    # Any value smaller than this is considered to be zero.
    zeroTol = 0.000001

    # How many times to iterate on the perimeter's shape.
    numIterations = 10000

    # How many perimeters to keep in the history.
    maxHistory = 88
    History = []

    # Note: Colors are designed for a black background so that
    # the last/oldest curve is invisible.
    # Default DB color is af6df0 = 170, 109, 240
    colorFirst = [255, 255, 255]
    colorLast = [0, 0, 0]

    # Compute the RGB range between the two colors.
    colorRange = []
    for i in range(0,3):
        colorRange.append(colorLast[i] - colorFirst[i])

    # Create a list containing a color for each entitiy in the history.
    # Each color is an RGB triplet blended from the first and last colors.
    # RGB is scaled between [0-1] not [0-255].
    colorHistory = []
    for c in range(0, maxHistory):
        f = c / (maxHistory - 1.0)
        rgb = []
        for i in range(0,3):
            c1 = colorFirst[i]
            cr = colorRange[i]
            rgb.append((c1 + f + cr) / 255.0)
        colorHistory.append(rgb)

    # Ask user to select a single domain.
    selMask = pw.Display.createSelectionMask(requireDomain="")
    selResults = GlyphVar()

    if not pw.Display.selectEntities(selResults, \
            description="Select a domain.", selectionmask=selMask, single=True):
        # Nothing was selected
        exit()
    else:
        # Get the selected domain from the selection results.
        glf.puts(str(selResults.value))
        domList = selResults["Domains"]
        domSelected = domList[0]

    # Initialize a bounding box.
    bbox = Extents()

    # Create a single DB line of the domain's perimeter grid points.
    # While doing this, compute the domain's bounding box for use in scaling.
    seg = pw.SegmentSpline()
    # For each connector on each edge of the domain
    # copy its grid points into the DB perimeter line
    numEdges = domSelected.getEdgeCount()
    for e in range(1, numEdges + 1):
        edge = domSelected.getEdge(e)
        numCons = edge.getConnectorCount()
        for c in range(1, numCons + 1):
            con = edge.getConnector(c)
            numPoints = con.getDimension()
            istart = 1
            if c > 1:
                # Don't duplicate the point shared by two cons on the same edge
                istart = 2
            elif (e > 1 and c == 1):
                # Don't duplicate the point at the node shared by edges.
                istart = 2
            for i in range(istart, numPoints + 1):
                P = con.getXYZ(grid=i)
                seg.addPoint(P)
                #update bounding box
                bbox = bbox.enclose(P)

    Perimeter = pw.Curve()
    Perimeter.addSegment(seg)
    History.append(Perimeter)

    # Save the original perimeter's bounding box for scaling calculations.
    bbSizeOrig = bbox.maximum() - bbox.minimum()

    # Iterate on the following:
    # Go around the perimeter and create a new perimeter
    # from the mid points of the line segments on the old perimeter.
    for i in range(1, numIterations + 1):
        #print(i)
        bbox = Extents()
        segNew = pw.SegmentSpline()
        segOld = Perimeter.getSegment(1)
        numPoints = segOld.getPointCount()
        # Create a point on the new segment at
        # the midpoint of two points on the old segment.
        for n in range(2, numPoints + 1):
            A = segOld.getPoint(n)
            B = segOld.getPoint(n - 1)
            Cx = (A[0] + B[0])/2
            Cy = (A[1] + B[1])/2
            Cz = (A[2] + B[2])/2
            P = [Cx, Cy, Cz]
            if n == 2:
                # Save this first point to re-use as the last point
                P1 = copy.deepcopy(P)
            segNew.addPoint(P)
            # Update the bounding box.
            bbox = bbox.enclose(P)
        # add the first point as the last point to close the perimeter
        segNew.addPoint(P1)
        newPerimeter = pw.Curve()
        newPerimeter.addSegment(segNew)
        # Compare the total length of the new and old perimeters
        # to see if we can quit if they're not changing too much.
        newLength = newPerimeter.getTotalLength()
        oldLength = Perimeter.getTotalLength()
        chgLength = abs(newLength - oldLength) / oldLength
        
        # Add the new perimeter to the end of the history.
        History.append(newPerimeter)
        if len(History) > maxHistory:
            # If the history is too long, delete the oldest and remove it.
            pw.Entity.delete(History[0])
            del History[0]
        # Update the current perimeter curve
        Perimeter = newPerimeter
        
        # set scale factors based on relative sizes of 
        # original and new perimeters
        bbSizeNew = bbox.maximum() - bbox.minimum()
        
        #print(pw.Vector3.X(bbSizeOrig))
        scaleFactorX = bbSizeOrig[0] / bbSizeNew[0]
        scaleFactorY = bbSizeOrig[1] / bbSizeNew[1]
        if abs(bbSizeNew[2]) < zeroTol:
            scaleFactorZ = 1.0
        else:
            scaleFactorZ = bbSizeOrig[2] / bbSizeNew[2]
        scaleFactor = [scaleFactorX, scaleFactorY, scaleFactorZ]
        # Scale around the center of the new perimeter's bounding box
        scaleAnchor = bbox.minimum() + bbSizeNew/2.0
        # The new perimeter has to be scaled up for visual reasons
        # otherwise it shrinks to nothing.
        xform = Transform.scaling(scaleFactor, scaleAnchor)
        pw.Entity.transform(xform, Perimeter)
        
        # Give each perimeter in the history a unique color.
        npoints = 0
        for p in History:
            p.setRenderAttribute("ColorMode", "Entity")
            p.setColor(colorHistory[npoints])
            npoints += 1
        # Update the display.
        pw.Display.update()

    # If all iterations complete, delete all but the last curve
    del History[-1]
    pw.Entity.delete(History)

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
