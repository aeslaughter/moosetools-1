#!/usr/bin/env python3
#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

import chigger
from chigger import geometric

window = chigger.Window(size=(600, 600))
viewport = chigger.Viewport(window)

box0 = geometric.Cube(viewport, center=(0.5,0.5,0.5), lengths=(1.,1.,1.), color=(0.25,0.5,0.75))
box1 = geometric.Cube(viewport, center=(0.25,0.25,0.25), lengths=(3.,2.,1.), color=(1,0.5,0.5))

#window.write('cube.png')
window.start()
