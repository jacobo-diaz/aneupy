# import os
# os.chdir(r"/home/jdiaz/Dropbox/code/aneupy")
# execfile(r"/home/jdiaz/Dropbox/code/aneupy/test.py")

# import aneupy

import Geometry
aneupy = reload(Geometry)

d = aneupy.Domain()

d.add_section(name='s1', origin=[0., 0., 0.])
d.add_section(name='s2', origin=[10., 0., 3.])

d.sections['s1'].add_circle(radius=5.)
d.sections['s1'].rotateX(angle=0.)

d.sections['s2'].add_circle(radius=4.)
d.sections['s2'].rotateX(angle=30.)


d.add_shell(name='S1', sections=['s1', 's2'])

# d.add_solid


# # display all objects in the current view (if possible)
# salome.sg.DisplayAll()
# salome.sg.UpdateView() # update view