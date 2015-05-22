# Testing ---------------------------------------------------------------------
# import os ; os.chdir(r"/home/jdiaz/Dropbox/code/aneupy/test") ; execfile(r"aneurysm_1_CAD.py")
# import os ; os.chdir("/home/jdiaz/aneupy/test") ; execfile(r"aneurysm_1_CAD.py")

import Abaqus
aneupy = reload(Abaqus)
# -----------------------------------------------------------------------------

# Production ------------------------------------------------------------------
# import aneupy
# -----------------------------------------------------------------------------

db = aneupy.Database()

f = aneupy.Model('aneurysm_fluid', cfd=True)
s = aneupy.Model('aneurysm_solid')

f.part_from_iges('aneurysm_fluid.iges')
f.part_from_iges('aneurysm_solid.iges')
s.part_from_iges('aneurysm_solid.iges')

f.create_set(name='outer_surface', coord=, entity_type=face|edge)
f.create_surface(name='outer_surface', coord=, entity_type=face|edge)
f.create_set(name='front_face')
f.create_set(name='end_face')

f.add_material('water', density=1000., viscosity=1.E-3)
f.add_material('blood', E=10, nu=.3)
s.add_material('flesh', E=20, nu=.3)

f.add_section(name='fluid', material='water')

f.assign_section(section='fluid', set|surface)

f.create_assembly()
s.create_assembly()

f.add_global_seed
f.add_local_seed(set|surface, elements, space, ...)

f.create_mesh()

f.add_step(name='fluid')

f.create_load
f.create_BC

# PRobar si cambiando las coordenadas del iges se cambia la posición en el assembly

# 3. Optionally, ensure matching nodes at the interface regions.
# 4. In each model, create a co-simulation interaction to specify the interface region and coupling schemes.
# 5. Create a co-execution to identify the two models involved and specify the job parameters for each analysis.
# 6. Submit the co-execution to perform the co-simulation.
# 7. View the results of the co-simulation using overlay plots.


db.save(file='aneurysm.cae')
