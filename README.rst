# Glyph API for Python

This is a Python implementation of the Pointwise Glyph API. Glyph is implemented as a set of Tcl procedures that have an object-oriented feel. Pointwise supports non-Tcl scripting (or binary code) applications through a feature called "Glyph Server", first avaialable in V18.0R1. This API leverages some of the introspective features of the Python language to automatically convert Python expressions into Glyph (Tcl) command strings to be executed on the Glyph Server, and to convert the results back into Python objects.

Glyph commands are formulated in Python using a JSON structure and passed to Glyph through a special dispatching command on the server that handles only JSON-encoded commands. (This dispatching command is available in Pointwise V18.2 and later.) The results from this command are returned as JSON structures that are subsequently processed and converted into Python number, string and special GlyphObj objects.

The heart of this API are the GlyphObj and GlyphVar classes. All Glyph objects and classes are represented as instances of GlyphObj, which provides transparent access to all Glyph actions as though they were implemented in Python. GlyphVar provides a way to set and access Tcl variables on the server, primarily for use with Glyph actions that accept Tcl variable names as arguments.

## Usage

The most basic usage of the Glyph API for Python is to:

1. Import GlyphClient from pointwise
2. Create GlyphClient object and connect to a listening Pointwise server
3. Request a GlyphAPI object from the client object
4. Issue Glyph actions through the GlyphAPI

### Example Usage

```python
from pointwise import GlyphClient
from pointwise.glyphapi import *

glf = GlyphClient(port=2807)
pw = glf.get_glyphapi()
    
pw.Connector.setCalculateDimensionMethod("Spacing")
pw.Connector.setCalculateDimensionSpacing(.3)
with pw.Application.begin("Create") as creator:
    conic1 = pw.SegmentConic()
    conic1.addPoint((-25,8,0))
    conic1.addPoint((-8,8,0))
    conic1.setIntersectPoint((-20,20,0))
    conic2 = pw.SegmentConic()
    conic2.addPoint(conic1.getPoint(conic1.getPointCount()))
    conic2.addPoint((10,16,0))
    conic2.setShoulderPoint((8,8,0))
    con = pw.Connector()
    con.addSegment(conic1)
    con.addSegment(conic2)
    con.calculateDimension()
    creator.end()
```

## Usage Notes

### GlyphClient object

A GlyphClient implements only the client-server communication from the Python script to a Pointwise server. It can be used completely independently from the GlyphAPI as it provides methods for connecting to a server, evaluating Tcl/Glyph expressions, retrieving the raw Tcl string results, and disconnecting from the server.

A GlyphClient can be used as a Python context manager. This allows a script to access a Pointwise Glyph server using idiomatic context management.

Example:

```python
with GlyphClient(port=2807) as glf:
    glf.eval("puts {Hello World}")
```

GlyphClient can run a Glyph server automatically as a subprocess by specifying the port as zero. Note that this will consume a Pointwise license, if one is available. Standard and error output from the server subprocess can be captured by specifying a callback function.

Example:

```python
def echo(text):
    print("Server:", text)

with GlyphClient(port=0, callback=echo) as glf:
    glf.puts("Hello World")
```

Should produce:

```
Server: Hello World
```

### GlyphAPI object

GlyphAPI extends the GlyphClient functionality by providing the transparent access needed to make Glyph calls in a very Pythonic manner. A GlyphAPI object should only be created by a connected GlyphClient object. Connections to multiple Pointwise servers are possible, and all Glyph actions invoked within the context of a GlyphAPI are done so on the associated server connection.

Example:
```python
glf1 = GlyphClient(port=2807)
glf2 = GlyphClient(port=2808)

pw1 = glf1.get_glyphapi()
pw2 = glf2.get_glyphapi()

con1 = pw1.GridEntity.getByName("con-1")
con2 = pw2.GridEntity.getByNAme("con-2")

con1.join(con2) # Behavior undefined
```

### GlyphVar object

A GlyphVar is required for Glyph actions that expect a Tcl variable name as an argument. These actions typically set the variable to some ancillary result value, independent of the action's direct result. A GlyphVar object is not coupled to a specific GlyphClient connection, as it is used only in the context of a Glyph action in order to retrieve some result value stored in a Tcl variable. A GlyphVar may be assigned a Tcl variable name, but it is not required; when unassigned, a unique temporary Tcl variable name will be generated.

Example:
```python
poleDoms = GlyphVar()
pw.BlockStructured.createFromDomains(doms, poleDomains=poleDoms)
for d in poleDoms.value: print(d.getName())
```

### GlyphObj object

GlyphObj is the primary Python interface to Glyph classes, objects and their associated actions. A GlyphObj instance is created automatically in the following ways:

* When the method name of a call to GlyphAPI matches a published Glyph class name
* When the result of some Glyph action returns a Glyph function name (object)
* When a GlyphVar contains a Glyph function name (object)
* When constructed directly using a Glyph function name (object)

Examples:
```python
# There are two GlyphObj instances created here, one for "pw::Connector" class
# and one for "::pw::Connector_1" object returned by pw.Connector()
con1 = pw.Connector()

# There are two GlyphObj instances created here as well, one for
# "pw::GridEntity" class and one for "::pw::Connector_1" object returned
# by "pw::GridEntity getByName con-1"
con2 = pw.GridEntity.getByName("con-1")

# This generates GlyphObj instances for "pw::BlockStructured", all the blocks
# returned by "createFromDomains" and all the domains (if any) returned in
# the "pdoms" Tcl variable passed to the action.
poleDoms = GlyphVar("pdoms")
blk = pw.BlockStructured.createFromDomains(doms, poleDomains=poleDoms)
for d in poleDoms.value: print(d.getName())
```

### Generating Glyph Actions Automatically

Glyph actions are basically method invocations on either a Glyph class or a Glyph function (object). (These are called 'functions' because Glyph generates a mapping from a Tcl proc to an internal object in order to simulate object-oriented behavior in Glyph.) There are two types of actions: static actions and instance actions. Further, every Glyph class that can be instantiated directly has a static "create" action. So, by exploiting Python introspective features, the following syntaxes generates an associated Tcl/Glyph command:

* A GlyphObj that represents a Glyph class that is called directly becomes a "create" action call. Arguments can be passed to the create action as needed.
* A method call on a GlyphObj that represents a Glyph class is translated into a static action call on the Glyph class.
* A method call on a GlyphObj that represents a Glyph object is translated into an instance action call on the object.

Example:
```python
# This invokes "pw::Connector create" with no arguments
con = pw.Connector()

# This invokes "pw::Examine create ConnectorLengthI"
exam = pw.Examine("ConnectorLengthI")

# This invokes "pw::Connector getAdjacentConnectors $cons"
cons = pw.Connector.getAdjacentConnectors(cons)

# This invokes "$con1 join $con2"
con1 = con1.join(con2)
```

### Passing Arguments and Flags to Glyph Actions

Many Glyph actions accept both positional and flag arguments. The Python equivalent of these are positional and _keyword_ arguments, but there are some strict requirements that must be followed in order for the action commands to be generated correctly. All positional arguments must appear first in the Python method invocation, as is the requirement of the language, followed by all optional keyword arguments. GlyphObj converts all keyword arguments in the following way:

* If the keyword does not end in an underscore ('\_'):
  * If the keyword argument is False, the flag is not added to the command
  * Otherwise, the keyword is prepended with a dash ('-') and added to the command. Then:
    * If the keyword argument is a bool and is True, no argument is added to the command
    * Otherwise, the keyword argument is added as a single element to the command
* If the keyword ends in an underscore:
  * The keyword is prepended with a dash, and the trailing underscore is removed, and the flag is added to the command. Then:
    * If the keyword argument is a list of values, each value is added as a separate command argument. Note that embedded lists will remain as lists in the Glyph action command.
    * Otherwise, the keyword argument is added to the command, even if a boolean value.

Note that any positional argument that is a list will be passed as a Tcl list in the command.

Examples:
```python
# set pt [$con getPosition -arc 1.0]
pt = con.getPosition(1.0, arc=True)

# set pt [$con getXYZ 1]
pt = con.getXYZ(1, arc=False)

# set ents [$bc getEntities -visibility true]
ents = bc.getEntities(visibility_=True)

# pw::Entity project -type Linear -axis {0 0 0} {0 0 1} $ents
pw.Entity.project(ents, type="Linear", axis_=[(0, 0, 0), (0, 0, 1)])

# $shape polygon -points { { 0 0 0 } { 0 1 0 } { 1 0 0 } }
shape.polygon(points=[(0, 0, 0), (0, 1, 0), (1, 0, 0)])
```

### Glyph Objects as Context Managers

In many cases it is convenient to use a GlyphObj that represents certain transient Glyph objects as Python context managers. Specifically, Glyph _Mode_ and _Examine_ objects are generally short-lived and are used in very specific contexts. For these Glyph object types only, context management is implemented in GlyphObj.

Examples:
```python
with pw.Application.begin("Create") as creator:
    con = pw.Connector()
    ...
    # a mode MUST be explicitly ended before the context exits, otherwise
    # it is aborted and all modifications made in the mode are discarded
    creator.end()

with pw.Examine("BlockJacobian") as exam:
    exam.addEntity([blk1, blk2])
    exam.examine()
    ...
    # Examine objects are automatically deleted when the context exits,
    # so nothing needs to be done explicitly
```

### Glyph Utility Classes

The standard Tcl/Glyph command set includes a number of utility classes to perform vector algebra, extent box computation, transformation matrices, etc. To improve the overall usefulness and speed of this API, these classes were implemented directly in Python, rather than through the Glyph Server. Many of the mathematical vector and matrix operations are performed using the 'numpy' package. These utilty classes include, along with their Glyph counterparts:

* ```Vector2 - pwu::Vector2```
* ```Vector3 - pwu::Vector3```
* ```Quaternion - pwu::Quaternion```
* ```Plane - pwu::Plane```
* ```Transform - pwu::Transform```
* ```Extents - pwu::Extents```

Nearly the complete set of functions documented at https://www.pointwise.com/glyph under the 'Utilities' section have been implemented as Python classes.

Example:

```python
# set v1 [pwu::Vector3 set { 0 1 2 }
v1 = Vector3([0, 1, 2])  # Vector3(0, 0, 0) also works

# set v2 [pwu::Vector3 add $v1 { 2 4 6 }
v2 = v1 + Vector3(2, 4, 6)

# set v3 [pwu::Vector3 cross $v1 $v2]
v3 = v1 * v2             # cross product

# set v3 [pwu::Vector3 normalize $v3]
v3 = v3.normalize()
```
