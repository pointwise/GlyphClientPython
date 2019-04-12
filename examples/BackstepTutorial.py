#
# Copyright 2018 (c) Pointwise, Inc.
# All rights reserved.
#
# This sample Python script is not supported by Pointwise, Inc.
# It is provided freely for demonstration purposes only.
# SEE THE WARRANTY DISCLAIMER AT THE BOTTOM OF THIS FILE.
#

""" This is an example script that generates the structured block topology
    of the Backward Step from the Pointwise Tutorial Workbook. This
    example uses the Glyph API for Python.

    For demonstration purposes, many of the Python commands are preceded
    by a comment that shows the equivalent Tcl command.  This script can
    be run in either Python 2.7+ or Python 3.6+.

    To run this example in Python 3.6+:
        - Start a Pointwise GUI instance
        - Go to Script, Glyph Server...
        - Set Listen Mode to Active
        - OK
        - Run 'python backstep.py' at a command prompt on the same host
          as the Pointwise instance
"""

from pointwise import GlyphClient
from pointwise.glyphapi import *

# Connect to the Pointwise server listening on localhost at port 2807 with
# no authentication token...

# glf = GlyphClient(port=2807)

# ... or create a pointwise server as a subprocess and connect to that.
# Note: this will consume a Pointwise license
def echo(line):
    print("Script: {0}".format(line), end='')  # Not Python 2.7 compatible

# Run in batch mode
glf = GlyphClient(port=0, callback=echo)

# Run in GUI, default port
# glf = GlyphClient(port=2807, callback=echo)

glf.connect()

# Use the Glyph API for Python
pw = glf.get_glyphapi()

# Allow error messages to be printed on the server
pw.Database._setVerbosity("Errors")
pw.Application._setVerbosity("Errors")

# Reset the server's workspace
pw.Application.setUndoMaximumLevels(10)
pw.Application.reset()
pw.Application.markUndoLevel("Journal Reset")

# pw::Connector setDefault Dimension 30
pw.Connector.setDefault("Dimension", 30)

# set creator [pw::Application begin Create]
with pw.Application.begin("Create") as creator:
    # set seg [pw::SegmentSpline create]
    seg = pw.SegmentSpline()

    # $seg addPoint {0 0 0}
    seg.addPoint((0, 0, 0))
    seg.addPoint((20, 0, 0))

    # set con [pw::Connector create]
    con = pw.Connector()

    # $con addSegment $seg
    con.addSegment(seg)

    # $con calculateDimension
    con.calculateDimension()

    # "$creator end" is implied

pw.Application.markUndoLevel("Create 2 Point Connector")

with pw.Application.begin("Create") as creator:
    seg = pw.SegmentSpline()
    seg.addPoint((20, 0, 0))
    seg.addPoint((60, 0, 0))
    con = pw.Connector()
    con.addSegment(seg)
    con.calculateDimension()

pw.Application.markUndoLevel("Create 2 Point Connector")

# pw::Display resetView -Z
pw.Display.resetView("-Z")

cons = { }
# set cons(con-1) [pw::GridEntity getByName "con-1"]
cons["con-1"] = pw.GridEntity.getByName("con-1")
cons["con-2"] = pw.GridEntity.getByName("con-2")

# set coll [pw::Collection create]
coll = pw.Collection()

# foreach { k v } [array get cons] { lappend clist $v }
# $coll set $clist
coll.set(cons.values())

# $coll do setRenderAttribute RenderMode Intervals
coll.do("setRenderAttribute", "RenderMode", "Intervals")

# $coll delete
coll.delete()

pw.Application.markUndoLevel("Modify Entity Display")

# set modifier [pw::Application begin Modify]
with pw.Application.begin("Modify", cons["con-1"]) as modifier:
    # [$cons(con-1) getDistribution 1] setBeginSpacing 1
    cons["con-1"].getDistribution(1).setBeginSpacing(1)

    # "$modifier end" is implied

pw.Application.markUndoLevel("Change Spacing")

with pw.Application.begin("Modify", cons.values()) as modifier:
    cons["con-1"].getDistribution(1).setEndSpacing(0.1)
    cons["con-2"].getDistribution(1).setEndSpacing(0.1)

pw.Application.markUndoLevel("Change Spacings")

with pw.Application.begin("Modify", cons["con-2"]) as modifier:
    cons["con-2"].getDistribution(1).setEndSpacing(2)

pw.Application.markUndoLevel("Change Spacing")

with pw.Application.begin("Create") as creator:
    # set edge [pw::Edge createFromConnectors -single $cons(con-2)]
    edge = pw.Edge.createFromConnectors(cons["con-2"], single=True)

    # set dom [pw::DomainuStructured create]
    dom = pw.DomainStructured()

    # $dom addEdge $edge
    dom.addEdge(edge)

# set extruder [pw::Application begin ExtrusionSolver $dom]
with pw.Application.begin("ExtrusionSolver", dom) as extruder:
    # $dom setExtrusionSolverAttribute Mode Translate
    dom.setExtrusionSolverAttribute("Mode", "Translate")

    # $dom setExtrusionSolverAttribute TranslateDirection {0 -1 0}
    dom.setExtrusionSolverAttribute("TranslateDirection", (0, -1, 0))

    # $dom setExtrusionSolverAttribute TranslateDistance 8
    dom.setExtrusionSolverAttribute("TranslateDistance", 8)

    # $extruder run 29
    extruder.run(29)

    # "$extruder end" is implied

pw.Application.markUndoLevel("Translate")

with pw.Application.begin("Create") as creator:
    edge = pw.Edge.createFromConnectors(cons.values(), single=True)
    dom = pw.DomainStructured()
    dom.addEdge(edge)

with pw.Application.begin("ExtrusionSolver", dom) as extruder:
    dom.setExtrusionSolverAttribute("Mode", "Translate")
    dom.setExtrusionSolverAttribute("TranslateDirection", Vector3(0, -1, 0).negate())
    dom.setExtrusionSolverAttribute("TranslateDistance", 20)
    extruder.run(29)

pw.Application.markUndoLevel("Translate")

cons["con-3"] = pw.GridEntity.getByName("con-3")
cons["con-5"] = pw.GridEntity.getByName("con-5")
cons["con-6"] = pw.GridEntity.getByName("con-6")
cons["con-8"] = pw.GridEntity.getByName("con-8")

with pw.Application.begin("Modify", cons.values()) as modifier:
    cons["con-3"].getDistribution(1).setBeginSpacing(0.1)
    cons["con-5"].getDistribution(1).setEndSpacing(0.1)
    cons["con-6"].getDistribution(1).setBeginSpacing(0.1)
    cons["con-8"].getDistribution(1).setEndSpacing(0.1)

pw.Application.markUndoLevel("Change Spacings")

doms = { }
doms["dom-1"] = pw.GridEntity.getByName("dom-1")
doms["dom-2"] = pw.GridEntity.getByName("dom-2")

# foreach { k v } [array get doms] { lappend dlist $v }
# set solver [pw::Application begin EllipticSolver $dlist]
with pw.Application.begin("EllipticSolver", doms.values()) as solver:
    # $solver Initialize
    solver.run("Initialize")
    # "$solver end" is implied

pw.Application.markUndoLevel("Initialize")

pw.Connector.setDefault("Dimension", 21)

# pw::Application setClipboard $dlist
pw.Application.setClipboard(doms.values())

# set paster [pw::Application begin Paste]
with pw.Application.begin("Paste") as paster:
    # set ents [$paster getEntities]
    ents = paster.getEntities()

    # set modifier [pw::Application begin Modify $ents]
    with pw.Application.begin("Modify", ents) as modifier:
        # set xforments [$modifier getEntities]
        xforments = modifier.getEntities()

        # set coll [pw::Collection create]
        coll = pw.Collection()

        # $coll set $xforments
        coll.set(xforments)

        # set xform [pw::Transform translation {0 0 15}]
        xform = Transform.translation((0, 0, 15))

        # pw::Entity transform $xform [$coll list]
        pw.Entity.transform(xform, coll.list())

        # $coll delete
        coll.delete()

        # "$modifier end" is implied

    # "$paster end" is implied

pw.Application.markUndoLevel("Paste")

pw.Display.setShowDomains(False)

with pw.Application.begin("Create") as creator:
    seg = pw.SegmentSpline()
    seg.addPoint(pw.GridEntity.getByName("con-13").getPosition(arc=0))
    seg.addPoint(pw.GridEntity.getByName("con-1").getPosition(arc=0))
    con = pw.Connector()
    con.addSegment(seg)
    con.calculateDimension()

pw.Application.markUndoLevel("Create 2 Point Connector")

with pw.Application.begin("Create") as creator:
    seg = pw.SegmentSpline()
    seg.addPoint(pw.GridEntity.getByName("con-9").getPosition(arc=0))
    seg.addPoint(pw.GridEntity.getByName("con-1").getPosition(arc=1))
    con = pw.Connector()
    con.addSegment(seg)
    con.calculateDimension()

pw.Application.markUndoLevel("Create 2 Point Connector")

with pw.Application.begin("Create") as creator:
    seg = pw.SegmentSpline()
    seg.addPoint(pw.GridEntity.getByName("con-4").getPosition(arc=1))
    seg.addPoint(pw.GridEntity.getByName("con-11").getPosition(arc=1))
    con = pw.Connector()
    con.addSegment(seg)
    con.calculateDimension()

pw.Application.markUndoLevel("Create 2 Point Connector")

with pw.Application.begin("Create") as creator:
    seg = pw.SegmentSpline()
    seg.addPoint(pw.GridEntity.getByName("con-10").getPosition(arc=1))
    seg.addPoint(pw.GridEntity.getByName("con-4").getPosition(arc=0))
    con = pw.Connector()
    con.addSegment(seg)
    con.calculateDimension()

pw.Application.markUndoLevel("Create 2 Point Connector")

with pw.Application.begin("Create") as creator:
    seg = pw.SegmentSpline()
    seg.addPoint(pw.GridEntity.getByName("con-2").getPosition(arc=1))
    seg.addPoint(pw.GridEntity.getByName("con-9").getPosition(arc=1))
    con = pw.Connector()
    con.addSegment(seg)
    con.calculateDimension()

pw.Application.markUndoLevel("Create 2 Point Connector")

with pw.Application.begin("Create") as creator:
    seg = pw.SegmentSpline()
    seg.addPoint(pw.GridEntity.getByName("con-14").getPosition(arc=1))
    seg.addPoint(pw.GridEntity.getByName("con-7").getPosition(arc=0))
    con = pw.Connector()
    con.addSegment(seg)
    con.calculateDimension()

pw.Application.markUndoLevel("Create 2 Point Connector")

with pw.Application.begin("Create") as creator:
    seg = pw.SegmentSpline()
    seg.addPoint(pw.GridEntity.getByName("con-7").getPosition(arc=1))
    seg.addPoint(pw.GridEntity.getByName("con-15").getPosition(arc=1))
    con = pw.Connector()
    con.addSegment(seg)
    con.calculateDimension()

pw.Application.markUndoLevel("Create 2 Point Connector")

pw.Display.setShowDomains(True)
pw.Display.resetView("-Z")

for con in pw.Grid.getAll(type="pw::Connector"):
    cons[con.getName()] = con

unusedCons = GlyphVar("unusedCons")
poleDoms = GlyphVar()
unusedDoms = GlyphVar()

# pw::DomainStructured createFromConnectors -reject unusedCons -solid $clist
pw.DomainStructured.createFromConnectors(cons.values(), reject=unusedCons, solid=True)

# pw::BlockStructured createFromDomains -poleDomains poleDoms -reject unusedDoms [pw::Grid getAll -type pw::Domain]
pw.BlockStructured.createFromDomains(pw.Grid.getAll(type="pw::Domain"), poleDomains=poleDoms, reject=unusedDoms)

# GlyphVar usage: 'var.value' is the processed Tcl variable, which may
# contain string or numeric values, or Glyph objects
if len(unusedDoms.value) > 0:
    glf.puts("First block assembly, some domains are unused:")
    for ud in unusedDoms.value:
        # print to the Pointwise message window
        glf.puts("   %s" % ud.getName())

if len(poleDoms.value) > 0:
    glf.puts("First block assembly, some domains are poles (fatal):")
    # foreach pd $poleDoms { puts [format "Domain %s is a pole domain" [$pd getName]] }
    for pd in poleDoms.value:
        glf.puts("   %s is a pole domain" % pd.getName())
    exit(1)

pw.Application.markUndoLevel("Assemble Blocks")

# The connection domain could not be automatically assembled from the full set of
# connectors, so we must isolate them and create the domain separately
connection_cons = []
for i in (2, 9, 18, 21): connection_cons.append(pw.GridEntity.getByName("con-%d" % i))

pw.DomainStructured.createFromConnectors(connection_cons, reject=unusedCons, solid=True)

pw.BlockStructured.createFromDomains(pw.Grid.getAll(type="pw::Domain"), poleDomains=poleDoms, reject=unusedDoms)

pw.Application.markUndoLevel("Assemble Blocks")

doms = { }
# foreach d [pw::Grid getAll -type pw::DomainStructured] { set doms([$d getName]) $d }
for d in pw.Grid.getAll(type="pw::DomainStructured"): doms[d.getName()] = d

blks = { }
# set blks(blk-1) [pw::GridEntity getByName "blk-1"]
blks["blk-1"] = pw.GridEntity.getByName("blk-1")

# set blks(blk-2) [pw::GridEntity getByName "blk-2"]
blks["blk-2"] = pw.GridEntity.getByName("blk-2")

# set bc [pw::BoundaryConditon create]
bc = pw.BoundaryCondition()

# $bc setName Inflow
bc.setName("Inflow")

# $bc setPhysicalType Inflow
bc.setPhysicalType("Inflow")

# $bc apply [list [list $blks(blk-2) $doms(dom-9)]]
bc.apply([[blks["blk-2"], doms["dom-9"]]])

bc = pw.BoundaryCondition()
bc.setName("Outflow")
bc.setPhysicalType("Outflow")

# $bc apply [list [list $blks(blk-2) $doms(dom-8)] [list $blks(blk-1) $doms(dom-5)]]
bc.apply([[blks["blk-2"], doms["dom-8"]], [blks["blk-1"], doms["dom-5"]]])

bc = pw.BoundaryCondition()
bc.setName("Wall")
bc.setPhysicalType("Wall")

bc.apply([[blks["blk-2"], doms["dom-7"]],
    [blks["blk-1"], doms["dom-6"]],
    [blks["blk-1"], doms["dom-10"]]])

bc = pw.BoundaryCondition()
bc.setName("Symmetry")
bc.setPhysicalType("Symmetry Plane")

bc.apply([[blks["blk-2"], doms["dom-4"]],
    [blks["blk-2"], doms["dom-2"]],
    [blks["blk-2"], doms["dom-11"]],
    [blks["blk-1"], doms["dom-1"]],
    [blks["blk-1"], doms["dom-3"]]])

pw.Application.markUndoLevel("Set BC")

# The remainder of this script is for demonstration purposes
# only, and is not part of the Back Step tutorial.

# set exam [pw::Examine create "BlockJacobian"]
with pw.Examine("BlockJacobian") as exam:
    # $exam addEntity $blist
    exam.addEntity(blks.values())

    # $exam examine
    exam.examine()

    # puts [format "Min/Max Jacobian: %f/%f" [$exam getMinimum] [$exam getMaximum]]
    glf.puts("Min/Max Jacobian: %f/%f" % (exam.getMinimum(), exam.getMaximum()))

    # Note: exam.delete() is optional since exam doubles as a context manager

# pw::CutPlane applyMetric BlockJacobian
pw.CutPlane.applyMetric("BlockJacobian")

# set cut [pw::CutPlane create]
cut = pw.CutPlane()

# $cut setConstant -J 11
cut.setConstant(J=11)

# $cut addBlock $blks(blk-1)
cut.addBlock(blks.values())

# $cut setTransparency 0.25
cut.setTransparency(0.25)

# $cut setShrinkFactor 0.9
cut.setShrinkFactor(0.9)

# pw::Application save backstep.pw
pw.Application.save("backstep.pw")

# foreach { k v } [array get blks] { lappend blist $v }
# pw::Application export -precision Single $blist backstep.cgns
pw.Application.export(blks.values(), "backstep.cgns", precision="Single")

glf.close()

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
