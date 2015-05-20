# PONER autoria


import os

# Abaqus Python modules
from abaqus import *
from abaqusConstants import *
from caeModules import *
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
from regionToolset import *
from odbAccess import *
from odbSection import *


class Model():

    def __init__(self, name, cfd=False, **kwargs):

        self.parts = {}
        self.instances = {}
        self.name = name
        self.cfd = cfd

        Mdb()

        for odb in session.odbs.values():
            odb.close()

        if self.cfd:
            self.model = mdb.Model(name=name, modelType=CFD)
        else:
            self.model = mdb.Model(name=name, modelType=STANDARD_EXPLICIT)

        if 'Model-1' in mdb.models:
            del mdb.models['Model-1']

    def save_model(self, path=None):
        if not path:
            path = self.name

        mdb.saveAs(pathName=path + '.cae')

    def part_from_iges(self, iges_file, name=None):

        if not name:
            name = os.path.splitext(os.path.basename(iges_file))[0]

        iges = mdb.openIges(iges_file, msbo=True, trimCurve=DEFAULT, scaleFromFile=OFF)

        self.parts[name] = self.model.PartFromGeometryFile(name=name,
            geometryFile=iges, combine=False, stitchTolerance=1.0,
            dimensionality=THREE_D, type=DEFORMABLE_BODY, convertToAnalytical=1, stitchEdges=1)

    def create_assembly(self):
        for name, part in self.parts.items():
            self.instances[name] = self.model.rootAssembly.Instance(name=name, part=part, dependent=ON)
