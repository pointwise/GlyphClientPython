from pointwise import GlyphClient
from pointwise.glyphapi import *

glyphVersion = '2.18.0'
growthRate = 1.3
conName = 'con-4'
port=0

print("Version =", glyphVersion)
print("Port =", port)
glf = GlyphClient(port=port, version=glyphVersion)
pw = glf.get_glyphapi()
print(glf._version)
pw.Application.reset()

value = pw.BlockUnstructured.getDefault("TRexGrowthRate")
print("Unstructured block T-Rex growth rate =", value)
if value != growthRate:
    raise Exception('Expected value to be ' + str(growthRate))
c1 = pw.Connector.create()
c2 = pw.Connector.create()
c3 = pw.Connector.create()
c4 = pw.Connector.create()
c2.delete()
c3.delete()
c4.delete()
c5 = pw.Connector.create()
name = c5.getName()
print("Connector name =", name)
if name != conName:
    raise Exception('Expected name to be ' + conName)

