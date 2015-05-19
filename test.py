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

d.add_shell(name='S1', sections=['s1', 's2', 's3', 's4', 's5'])

d.add_section(name='a1', origin=[0., 0., 0.])
d.add_section(name='a1a', origin=[0., 0., 10.])
d.add_section(name='a2', origin=[0., 0., 20.])
d.add_section(name='a2a', origin=[0., 0., 30.])
d.add_section(name='a3', origin=[0., 4., 50.])
d.add_section(name='a4a', origin=[0., 0., 70.])
d.add_section(name='a4', origin=[0., 0., 80.])
d.add_section(name='a5a', origin=[0., 0., 90.])
d.add_section(name='a5', origin=[0., 0., 100.])

d.sections['a1'].add_circle(radius=5.)
d.sections['a1a'].add_circle(radius=5.)
d.sections['a2'].add_circle(radius=5.)
d.sections['a2a'].add_circle(radius=7.)
d.sections['a3'].add_circle(radius=12.5)
d.sections['a4a'].add_circle(radius=7.)
d.sections['a4'].add_circle(radius=5.)
d.sections['a5a'].add_circle(radius=5.)
d.sections['a5'].add_circle(radius=5.)

# d.add_shell(name='A1', sections=['a1', 'a1a', 'a2', 'a2a', 'a3', 'a4a', 'a4', 'a5a', 'a5'], minBSplineDegree=2, maxBSplineDegree=5, approximation=True)
# d.add_shell(name='A1b', sections=['a1', 'a1a', 'a2', 'a2a', 'a3', 'a4a', 'a4', 'a5a', 'a5'], minBSplineDegree=2, maxBSplineDegree=20, approximation=True)
d.add_shell(name='aneurysm_outer', sections=['a1', 'a1a', 'a2', 'a2a', 'a3', 'a4a', 'a4', 'a5a', 'a5'], minBSplineDegree=10, maxBSplineDegree=20, approximation=True)
# d.add_shell(name='A1d', sections=['a1', 'a1a', 'a2', 'a2a', 'a3', 'a4a', 'a4', 'a5a', 'a5'], minBSplineDegree=10, maxBSplineDegree=20, approximation=False)

d.add_section(name='b1', origin=[0., 0., 0.])
d.add_section(name='b1a', origin=[0., 0., 10.])
d.add_section(name='b2', origin=[0., 0., 20.])
d.add_section(name='b2a', origin=[0., 0., 30.])
d.add_section(name='b3', origin=[0., 4., 50.])
d.add_section(name='b4a', origin=[0., 0., 70.])
d.add_section(name='b4', origin=[0., 0., 80.])
d.add_section(name='b5a', origin=[0., 0., 90.])
d.add_section(name='b5', origin=[0., 0., 100.])

d.sections['b1'].add_circle(radius=4.5)
d.sections['b1a'].add_circle(radius=4.5)
d.sections['b2'].add_circle(radius=4.5)
d.sections['b2a'].add_circle(radius=6.7)
d.sections['b3'].add_circle(radius=12.3)
d.sections['b4a'].add_circle(radius=6.7)
d.sections['b4'].add_circle(radius=4.5)
d.sections['b5a'].add_circle(radius=4.5)
d.sections['b5'].add_circle(radius=4.5)

d.add_shell(name='aneurysm_inner', sections=['b1', 'b1a', 'b2', 'b2a', 'b3', 'b4a', 'b4', 'b5a', 'b5'], minBSplineDegree=10, maxBSplineDegree=20, approximation=True)

d.add_solid_from_shell(name='aneurysm_outer', shell='aneurysm_outer')

d.add_solid_from_shell(name='aneurysm_inner', shell='aneurysm_inner')
d.add_solid_from_cut(name='aneurysm_outer', solids=['aneurysm_outer', 'aneurysm_inner'])

d.export_iges(solid='aneurysm_outer', file='/home/jdiaz/aneurysm_outer.iges')
d.export_iges(solid='aneurysm_inner', file='/home/jdiaz/aneurysm_inner.iges')
