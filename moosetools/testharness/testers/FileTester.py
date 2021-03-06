#* This file is part of MOOSETOOLS repository
#* https://www.github.com/idaholab/moosetools
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moosetools/blob/main/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

from moosetools.testharness.testers.RunApp import RunApp
from moosetools.testharness import util


# Classes that derive from this class are expected to write
# output files. The Tester::getOutputFiles() method should
# be implemented for all derived classes.
class FileTester(RunApp):
    @staticmethod
    def validParams():
        params = RunApp.validParams()
        params.addParam(
            'gold_dir', 'gold',
            "The directory where the \"golden standard\" files reside relative to the TEST_DIR: (default: ./gold/)"
        )
        params.addParam('abs_zero', 1e-10, "Absolute zero cutoff used in exodiff comparisons.")
        params.addParam('rel_err', 5.5e-6, "Relative error value used in exodiff comparisons.")
        return params

    def __init__(self, *args, **kwargs):
        RunApp.__init__(self, *args, **kwargs)

    def prepare(self, options):
        if self.specs['delete_output_before_running']:
            util.deleteFilesAndFolders(self.getTestDir(), self.getOutputFiles(),
                                       self.specs['delete_output_folders'])
