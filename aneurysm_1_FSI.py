# import aneupy

import Abaqus
aneupy = reload(Abaqus)

m = aneupy.Model('aneurysm', cfd=True)

m.part_from_iges('aneurysm_solid.iges')
m.part_from_iges('aneurysm_fluid.iges')

m.create_assembly()

m.save_model()
