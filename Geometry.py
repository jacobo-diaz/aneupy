import salome
import GEOM
from salome.geom import geomBuilder
import math

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

    def add_section(self, name, origin, OX_LCS=None, OY_LCS=None):

        self.sections[name] = Section(name, origin, OX_LCS, OY_LCS)

    def add_shell(self, name, sections, **kwargs):

        sections_list = []
        for section in sections:
            sections_list.append(self.sections[section])

        self.shells[name] = Shell(name, sections_list, **kwargs)

    def add_solid_from_shell(self, name, shell):

        solid = geompy.MakeSolid([self.shells[shell].shell])
        self.solids[name] = Solid(name, solid)

    def add_solid_from_cut(self, name, solids):

        solid = geompy.MakeCut(self.solids[solids[0]].solid, self.solids[solids[1]].solid, checkSelfInte=True)
        self.solids[name] = Solid(name, solid)

    def export_iges(self, solid, file):

        geompy.ExportIGES(self.solids[solid].solid, file, theVersion='5.3')


class Section():
    """ Defines a cross section.

        Cross sections are defined in the XY plane and then are transformed to
        the local coordinate system (LCS) defined with origin and OX_LCS and OY_LCS

        Origin is mandatory and the default LCS is the global coordinate system (GCS)

        OX_LCS is a sequence with the three components of LCS OX direction in GCS
        OY_LCS is a sequence with the three components of LCS OY direction in GCS

    """

    def __init__(self, name, origin, OX_LCS, OY_LCS):
        self.name = name
        self.origin = list(origin)
        self.bases = {}
        self.folder = geompy.NewFolder(name)

        try:
            self.OX_LCS = list(OX_LCS)
        except:
            self.OX_LCS = [1., 0., 0.]

        try:
            self.OY_LCS = list(OY_LCS)
        except:
            self.OY_LCS = [0., 1., 0.]

        # Create a vertex in the origin of the LCS
        self.location = geompy.MakeVertex(*tuple(self.origin))
        geompy.addToStudy(self.location, self.name + '_origin')
        geompy.PutToFolder(self.location, self.folder)

        # Create LCS for the section
        self.LCS = geompy.MakeMarker(*tuple(self.origin + self.OX_LCS + self.OY_LCS))
        self._obtain_rotation_matrix_LCS()
        geompy.addToStudy(self.LCS, self.name + '_LCS')
        geompy.PutToFolder(self.LCS, self.folder)
        salome.sg.updateObjBrowser(True)

    def _obtain_rotation_matrix_LCS(self):
        """ Obtains the rotation matrix R of the LCS and the
            Euler's angle and axis of the transformation"""

        _temp = geompy.GetPosition(self.LCS)
        rx = _temp[6:9]
        rz = _temp[3:6]
        vx = geompy.MakeVectorDXDYDZ(*rx)
        vz = geompy.MakeVectorDXDYDZ(*rz)
        vy = geompy.CrossProduct(vz, vx)
        ry = geompy.VectorCoordinates(vy)
        R = [list(rx), list(ry), list(rz)]

        eangle = math.acos(0.5*(R[0][0]+R[1][1]+R[2][2]-1.))
        if abs(eangle) > 1.E-2:
            eaxis = [(R[2][1]-R[1][2])/(2.*math.sin(eangle)),
                     (R[0][2]-R[2][0])/(2.*math.sin(eangle)),
                     (R[1][0]-R[0][1])/(2.*math.sin(eangle)),
                     ]
            eaxisv = geompy.MakeVectorDXDYDZ(*eaxis)
        else:
            eaxis = [0, 0, 0]
            eaxisv = None

        self.R = R
        self.EulerAngle = eangle
        self.EulerAngleDeg = eangle*180./math.pi
        self.EulerAxis = eaxis
        self.EulerAxisVector = eaxisv

    def _transform_bases_to_LCS(self):
        """ Transforms all bases to the LCS"""

        for base in self.bases.values():
            if self.EulerAxisVector:
                geompy.Rotate(base, self.EulerAxisVector, -self.EulerAngle)

            geompy.TranslateDXDYDZ(base, *tuple(self.origin))

    def _transform_bases_to_GCS(self):
        """ Transforms all bases to the GCS"""

        for base in self.bases.values():
            geompy.TranslateDXDYDZ(base, *tuple([-i for i in self.origin]))

            if self.EulerAxisVector:
                geompy.Rotate(base, self.EulerAxisVector, self.EulerAngle)

    def rotateX(self, angle):
        """Rotate the section around an axis parallel to global X
        through the origin of the LCS"""

        axis = geompy.MakeVectorDXDYDZ(1., 0, 0)
        axis = geompy.TranslateDXDYDZ(axis, *tuple(self.origin))
        geompy.Rotate(self.LCS, axis, angle*math.pi/180.)
        self._transform_bases_to_GCS()
        self._obtain_rotation_matrix_LCS()
        self._transform_bases_to_LCS()

    def rotateY(self, angle):
        """Rotate the section around an axis parallel to global Y
        through the origin of the LCS"""

        axis = geompy.MakeVectorDXDYDZ(0., 1., 0)
        axis = geompy.TranslateDXDYDZ(axis, *tuple(self.origin))
        geompy.Rotate(self.LCS, axis, angle*math.pi/180.)
        self._transform_bases_to_GCS()
        self._obtain_rotation_matrix_LCS()
        self._transform_bases_to_LCS()

    def rotateZ(self, angle):
        """Rotate the section around an axis parallel to global Z
        through the origin of the LCS"""

        axis = geompy.MakeVectorDXDYDZ(0., 0., 1.)
        axis = geompy.TranslateDXDYDZ(axis, *tuple(self.origin))
        geompy.Rotate(self.LCS, axis, angle*math.pi/180.)
        self._transform_bases_to_GCS()
        self._obtain_rotation_matrix_LCS()
        self._transform_bases_to_LCS()

    def add_circle(self, radius):
        self.bases['edge'] = geompy.MakeCircleR(radius)
        self.bases['face'] = geompy.MakeFaceWires([self.bases['edge']], isPlanarWanted=True)
        self.bases['shell'] = geompy.MakeShell([self.bases['face']])

        self._transform_bases_to_LCS()

        for key, base in self.bases.items():
            geompy.addToStudy(base, self.name + '_base_' + key)
            geompy.PutToFolder(base, self.folder)

        salome.sg.updateObjBrowser(True)


class Shell():

    def __init__(self, name, sections, closed=True, minBSplineDegree=2, maxBSplineDegree=5, approximation=True):
        self.name, self.sections = name, sections
        self.folder = geompy.NewFolder(self.name)

        self.edges = []
        self.shells = []
        self.locations = []

        theMinDeg = minBSplineDegree
        theMaxDeg = maxBSplineDegree
        theTol2D = 1.E-5
        theTol3D = 1.E-5
        theNbIter = 100
        theMethod = GEOM.FOM_Default
        isApprox = approximation

        sewing_precision = 1.E-4

        for section in self.sections:
            self.edges.append(section.bases['edge'])
            self.shells.append(section.bases['shell'])
            self.locations.append(section.location)

        self.compound = geompy.MakeCompound(self.edges)
        self.face = geompy.MakeFilling(self.compound, theMinDeg, theMaxDeg, theTol2D, theTol3D, theNbIter, theMethod, isApprox)

        if closed:
            sewing = geompy.MakeSewing([self.face, self.sections[0].bases['shell'], self.sections[-1].bases['shell']], sewing_precision)
            self.shell = geompy.MakeShell([sewing])
        else:
            self.shell = geompy.MakeShell([self.face])

        geompy.addToStudy(self.shell, self.name + '_shell')
        geompy.addToStudy(self.compound, self.name + '_compound')
        geompy.PutToFolder(self.shell, self.folder)
        geompy.PutToFolder(self.compound, self.folder)

        salome.sg.updateObjBrowser(True)


class Solid():

    def __init__(self, name, solid):
        self.name = name
        self.solid = solid
        self.folder = geompy.NewFolder(self.name)

        geompy.addToStudy(self.solid, self.name + '_solid')
        geompy.PutToFolder(self.solid, self.folder)

        salome.sg.updateObjBrowser(True)
