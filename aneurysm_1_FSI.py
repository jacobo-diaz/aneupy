# import aneupy

import Abaqus
aneupy = reload(Abaqus)

m = aneupy.Model('aneurysm', cfd=True)

m.part_from_iges('aneurysm_outer.iges')
m.part_from_iges('aneurysm_inner.iges')

m.create_assembly()

m.save_model()
