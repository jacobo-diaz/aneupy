import salome
import GEOM
from salome.geom import geomBuilder

salome.salome_init()
geompy = geomBuilder.New(salome.myStudy)

geompy.addToStudyAuto(0)


class Domain():

    def __init__(self, **kwargs):
        self.sections = {}
        self.shells = {}
        self.solids = {}

        O = geompy.MakeVertex(0, 0, 0)
        OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
        OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
        OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)

    def add_section(self, name, origin):

        self.sections[name] = Section(name, origin)

    def add_shell(self, name, sections):

        self.shells[name] = Shell(name, sections)


class Section():

    def __init__(self, name, origin):
        self.name, self.origin = name, origin

        _temp = geompy.MakeVertex(*tuple(self.origin))
        geompy.addToStudy(_temp, self.name)
        salome.sg.updateObjBrowser(True)

    def add_circle(self, radius):
        # salome commands
        pass

    def rotateX(self, angle):
        pass


class Shell():

    def __init__(self, name, sections):
        self.name, self.sections = name, sections
