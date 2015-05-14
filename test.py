# import os
# os.chdir(r"/home/jdiaz/Dropbox/code/aneupy")
# execfile(r"/home/jdiaz/Dropbox/code/aneupy/test.py")

# import aneupy

import Geometry
aneupy = reload(Geometry)

d = aneupy.Domain()

# d.add_section(name='s1', origin=[0., 0., 0.], OX_LCS=[0., 1., 0.], OY_LCS=[1., 0., 0.])
# d.add_section(name='s1', origin=[0., 0., 0.])
d.add_section(name='s2', origin=[0., 5., 10.])
# d.add_section(name='s3', origin=[0., 0., 0.])
# d.add_section(name='s3', origin=[0., 0., 20.], OX_LCS=[1., 1., 1.], OY_LCS=[0., 1., 0.])


# d.sections['s1'].add_circle(radius=5.)
# d.sections['s1'].rotateX(angle=45.)

d.sections['s2'].rotateX(angle=45.)
# d.sections['s2'].rotateY(angle=45.)
# d.sections['s2'].rotateZ(angle=30.)
d.sections['s2'].add_circle(radius=4.)
d.sections['s2'].rotateZ(angle=45.)

# d.sections['s3'].rotateX(angle=60.)


# d.add_shell(name='S1', sections=['s1', 's2'])

# d.add_solid


# # display all objects in the current view (if possible)
# salome.sg.DisplayAll()
# salome.sg.UpdateView() # update view