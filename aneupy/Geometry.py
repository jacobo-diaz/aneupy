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

    def add_shell(self, name, sections):

        self.shells[name] = Shell(name, sections)


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
        self.bases = []

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

        # Create LCS for the section
        self.LCS = geompy.MakeMarker(*tuple(self.origin + self.OX_LCS + self.OY_LCS))
        self._obtain_rotation_matrix_LCS()
        geompy.addToStudy(self.LCS, self.name + '_LCS')
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

    def _transform_base_to_LCS(self, base):
        """ Transforms a base to the LCS"""

        geompy.Rotate(base, self.EulerAxisVector, -self.EulerAngle)
        geompy.TranslateDXDYDZ(base, *tuple(self.origin))

    def _transform_bases_to_LCS(self):
        """ Transforms all bases to the LCS"""

        for base in self.bases:
            geompy.Rotate(base, self.EulerAxisVector, -self.EulerAngle)
            geompy.TranslateDXDYDZ(base, *tuple(self.origin))

    def _transform_bases_to_GCS(self):
        """ Transforms all bases to the GCS"""

        for base in self.bases:
            geompy.TranslateDXDYDZ(base, *tuple([-i for i in self.origin]))
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
        base = geompy.MakeCircleR(radius)
        self._transform_base_to_LCS(base)
        self.bases.append(base)
        geompy.addToStudy(self.bases[-1], self.name + '_base_' + str(len(self.bases)))
        salome.sg.updateObjBrowser(True)


class Shell():

    def __init__(self, name, sections):
        self.name, self.sections = name, sections
