# import os
# os.chdir(r"/home/jdiaz/Dropbox/code/aneupy")
# execfile(r"/home/jdiaz/Dropbox/code/aneupy/test.py")

# import aneupy

import Geometry
aneupy = reload(Geometry)

d = aneupy.Domain()

d.add_section(name='s1', origin=[0., 0., 0.])
d.add_section(name='s2', origin=[0., 0., 50.])
d.add_section(name='s3', origin=[50., 0., 60.])
d.add_section(name='s4', origin=[100., 0., 60.])
d.add_section(name='s5', origin=[120., 30., 80.])

d.sections['s1'].add_circle(radius=5.)
d.sections['s2'].add_circle(radius=4.)
d.sections['s3'].add_circle(radius=4.)
d.sections['s3'].rotateY(angle=90.)
d.sections['s4'].add_circle(radius=6.)
d.sections['s4'].rotateY(angle=90.)
d.sections['s5'].add_circle(radius=5.)
d.sections['s5'].rotateX(angle=90.)

d.add_shell(name='aneurysm_2', sections=['s1', 's2', 's3', 's4', 's5'])
d.add_solid_from_shell(name='aneurysm_2', shell='aneurysm_2')
d.export_iges(solid='aneurysm_2', file='aneurysm_2.iges')