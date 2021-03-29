#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
#pylint: enable=missing-docstring
from .TextBase import TextBase

class Text(TextBase):

    @staticmethod
    def validOptions():
        opt = TextBase.validOptions()
        opt.add('text', vtype=str, required=True, doc="The text to display.")
        return opt

    def _onRequestInformation(self, *args):
        self.assignOption('text', self._vtkactor.SetInput)
        TextBase._onRequestInformation(self, *args)
