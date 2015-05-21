# Testing ---------------------------------------------------------------------
# import os ; os.chdir(r"/home/jdiaz/Dropbox/code/aneupy/test") ; execfile(r"aneurysm_1_CAD.py")
# import os ; os.chdir("/home/jdiaz/aneupy/test") ; execfile(r"aneurysm_1_CAD.py")

import Abaqus
aneupy = reload(Abaqus)
# -----------------------------------------------------------------------------

# Production ------------------------------------------------------------------
# import aneupy
# -----------------------------------------------------------------------------

m = aneupy.Model('aneurysm', cfd=True)

m.part_from_iges('aneurysm_solid.iges')
m.part_from_iges('aneurysm_fluid.iges')

m.create_assembly()

m.save_model()
