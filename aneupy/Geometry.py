import os
import math
import cPickle as pickle

import salome
import GEOM
from salome.geom import geomBuilder


class Domain():

    def __init__(self, **kwargs):

        self.sections = {}
        self.shells = {}
        self.solids = {}

        if salome.myStudyManager.GetOpenStudies():
            study = salome.myStudyManager.GetStudyByName(salome.myStudyManager.GetOpenStudies()[0])
            salome.myStudyManager.Close(study)

        self.study = salome.myStudyManager.NewStudy('study')

        self.geompy = geomBuilder.New(self.study)
        self.geompy.addToStudyAuto(0)

        O = self.geompy.MakeVertex(0, 0, 0)
        OX = self.geompy.MakeVectorDXDYDZ(1, 0, 0)
        OY = self.geompy.MakeVectorDXDYDZ(0, 1, 0)
        OZ = self.geompy.MakeVectorDXDYDZ(0, 0, 1)

    def add_section(self, name, **kwargs):

        self.sections[name] = Section(name, **kwargs)

    def add_shell(self, name, sections, **kwargs):

        sections_list = []
        for section in sections:
            sections_list.append(self.sections[section])

        self.shells[name] = Shell(name, sections_list, **kwargs)

    def add_solid_from_shell(self, name, shell, **kwargs):

        solid = self.geompy.MakeSolid([self.shells[shell].shell])
        self.solids[name] = Solid(name, solid, **kwargs)

    def add_solid_from_cut(self, name, solids, **kwargs):

        solid = self.geompy.MakeCut(self.solids[solids[0]].solid, self.solids[solids[1]].solid, checkSelfInte=True)
        self.solids[name] = Solid(name, solid, **kwargs)

    def export_iges(self, solid, file):

        self.geompy.ExportIGES(self.solids[solid].solid, file, theVersion='5.3')

    def save(self, file):

        file_path = os.path.dirname(file)

        # Save SALOME study
        file_extension = '.hdf'
        file_name = os.path.basename(file.rsplit(file_extension, 1)[0])

        salome.myStudyManager.SaveAs(os.path.join(file_path, file_name + file_extension), self.study, False)

        # Save Python dictionary with CAD information
        self.cad = {}

        # geompy.BasicProperties -> [theLength, theSurfArea, theVolume]
        # geompy.Inertia  -> [I11,I12,I13, I21,I22,I23, I31,I32,I33, Ix,Iy,Iz]
        # geompy.PointCoordinates(geompy.MakeCDG())  -> CDG

        file_extension = '.cad'
        file_name = os.path.basename(file.rsplit(file_extension, 1)[0])

        with open(os.path.join(file_path, file_name + file_extension), 'wb') as output:
            # pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.name, output)


class Section():
    """ Defines a cross section.

        Cross sections are defined in the XY plane and then are transformed to
        the local coordinate system (LCS) defined with origin and OX_LCS and OY_LCS

        Origin is mandatory and the default LCS is the global coordinate system (GCS)

        OX_LCS is a sequence with the three components of LCS OX direction in GCS
        OY_LCS is a sequence with the three components of LCS OY direction in GCS

    """

    def __init__(self, name, origin, OX_LCS=None, OY_LCS=None, folder=True):
        self.name = name
        self.origin = list(origin)
        self.bases = {}

        self.study = salome.myStudyManager.GetStudyByName(salome.myStudyManager.GetOpenStudies()[0])
        self.geompy = geomBuilder.New(self.study)

        if folder:
            self.folder = self.geompy.NewFolder('section_' + name)
        else:
            self.folder = None

        try:
            self.OX_LCS = list(OX_LCS)
        except:
            self.OX_LCS = [1., 0., 0.]

        try:
            self.OY_LCS = list(OY_LCS)
        except:
            self.OY_LCS = [0., 1., 0.]

        # Create a vertex in the origin of the LCS
        self.location = self.geompy.MakeVertex(*tuple(self.origin))
        self.geompy.addToStudy(self.location, self.name + '_origin')
        if self.folder:
            self.geompy.PutToFolder(self.location, self.folder)

        # Create LCS for the section
        self.LCS = self.geompy.MakeMarker(*tuple(self.origin + self.OX_LCS + self.OY_LCS))
        self._obtain_rotation_matrix_LCS()
        self.geompy.addToStudy(self.LCS, self.name + '_LCS')
        if self.folder:
            self.geompy.PutToFolder(self.LCS, self.folder)

        salome.sg.updateObjBrowser(True)

    def _obtain_rotation_matrix_LCS(self):
        """ Obtains the rotation matrix R of the LCS and the
            Euler's angle and axis of the transformation"""

        _temp = self.geompy.GetPosition(self.LCS)
        rx = _temp[6:9]
        rz = _temp[3:6]
        vx = self.geompy.MakeVectorDXDYDZ(*rx)
        vz = self.geompy.MakeVectorDXDYDZ(*rz)
        vy = self.geompy.CrossProduct(vz, vx)
        ry = self.geompy.VectorCoordinates(vy)
        R = [list(rx), list(ry), list(rz)]

        eangle = math.acos(0.5*(R[0][0]+R[1][1]+R[2][2]-1.))
        if abs(eangle) > 1.E-2:
            eaxis = [(R[2][1]-R[1][2])/(2.*math.sin(eangle)),
                     (R[0][2]-R[2][0])/(2.*math.sin(eangle)),
                     (R[1][0]-R[0][1])/(2.*math.sin(eangle)),
                     ]
            eaxisv = self.geompy.MakeVectorDXDYDZ(*eaxis)
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
                self.geompy.Rotate(base, self.EulerAxisVector, -self.EulerAngle)

            self.geompy.TranslateDXDYDZ(base, *tuple(self.origin))

    def _transform_bases_to_GCS(self):
        """ Transforms all bases to the GCS"""

        for base in self.bases.values():
            self.geompy.TranslateDXDYDZ(base, *tuple([-i for i in self.origin]))

            if self.EulerAxisVector:
                self.geompy.Rotate(base, self.EulerAxisVector, self.EulerAngle)

    def rotateX(self, angle):
        """Rotate the section around an axis parallel to global X
        through the origin of the LCS"""

        axis = self.geompy.MakeVectorDXDYDZ(1., 0, 0)
        axis = self.geompy.TranslateDXDYDZ(axis, *tuple(self.origin))
        self.geompy.Rotate(self.LCS, axis, angle*math.pi/180.)
        self._transform_bases_to_GCS()
        self._obtain_rotation_matrix_LCS()
        self._transform_bases_to_LCS()

    def rotateY(self, angle):
        """Rotate the section around an axis parallel to global Y
        through the origin of the LCS"""

        axis = self.geompy.MakeVectorDXDYDZ(0., 1., 0)
        axis = self.geompy.TranslateDXDYDZ(axis, *tuple(self.origin))
        self.geompy.Rotate(self.LCS, axis, angle*math.pi/180.)
        self._transform_bases_to_GCS()
        self._obtain_rotation_matrix_LCS()
        self._transform_bases_to_LCS()

    def rotateZ(self, angle):
        """Rotate the section around an axis parallel to global Z
        through the origin of the LCS"""

        axis = self.geompy.MakeVectorDXDYDZ(0., 0., 1.)
        axis = self.geompy.TranslateDXDYDZ(axis, *tuple(self.origin))
        self.geompy.Rotate(self.LCS, axis, angle*math.pi/180.)
        self._transform_bases_to_GCS()
        self._obtain_rotation_matrix_LCS()
        self._transform_bases_to_LCS()

    def add_circle(self, radius):
        self.bases['edge'] = self.geompy.MakeCircleR(radius)
        self.bases['face'] = self.geompy.MakeFaceWires([self.bases['edge']], isPlanarWanted=True)
        self.bases['shell'] = self.geompy.MakeShell([self.bases['face']])

        self._transform_bases_to_LCS()

        for key, base in self.bases.items():
            self.geompy.addToStudy(base, self.name + '_base_' + key)
            if self.folder:
                self.geompy.PutToFolder(base, self.folder)

        salome.sg.updateObjBrowser(True)


class Shell():

    def __init__(self, name, sections, folder=False, closed=True, minBSplineDegree=2, maxBSplineDegree=5, approximation=True):
        self.name, self.sections = name, sections

        self.edges = []
        self.shells = []
        self.locations = []

        self.study = salome.myStudyManager.GetStudyByName(salome.myStudyManager.GetOpenStudies()[0])
        self.geompy = geomBuilder.New(self.study)

        if folder:
            self.folder = self.geompy.NewFolder('shell_' + name)
        else:
            self.folder = None

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

        self.compound = self.geompy.MakeCompound(self.edges)
        self.face = self.geompy.MakeFilling(self.compound, theMinDeg, theMaxDeg, theTol2D, theTol3D, theNbIter, theMethod, isApprox)

        if closed:
            sewing = self.geompy.MakeSewing([self.face, self.sections[0].bases['shell'], self.sections[-1].bases['shell']], sewing_precision)
            self.shell = self.geompy.MakeShell([sewing])
        else:
            self.shell = self.geompy.MakeShell([self.face])

        self.geompy.addToStudy(self.shell, self.name)
        self.geompy.addToStudy(self.compound, self.name + '_sections')

        if self.folder:
            self.geompy.PutToFolder(self.shell, self.folder)
            self.geompy.PutToFolder(self.compound, self.folder)

        salome.sg.updateObjBrowser(True)


class Solid():

    def __init__(self, name, solid, folder=False):
        self.name = name
        self.solid = solid

        self.study = salome.myStudyManager.GetStudyByName(salome.myStudyManager.GetOpenStudies()[0])
        self.geompy = geomBuilder.New(self.study)

        if folder:
            self.folder = self.geompy.NewFolder('solid_' + name)
        else:
            self.folder = None

        self.geompy.addToStudy(self.solid, self.name)

        if self.folder:
            self.geompy.PutToFolder(self.solid, self.folder)

        salome.sg.updateObjBrowser(True)
