#* This file is part of MOOSETOOLS repository
#* https://www.github.com/idaholab/moosetools
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moosetools/blob/main/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

import os, sys
from moosetools.testharness.testers.FileTester import FileTester
from moosetools.testharness import util


class AnalyzeJacobian(FileTester):
    @staticmethod
    def validParams():
        params = FileTester.validParams()
        #params.addRequiredParam('input',  "The input file to use for this test.")
        #params.addParam('test_name',      "The name of the test - populated automatically")
        #params.addParam('expect_out',     "A regular expression that must occur in the input in order for the test to be considered passing.")
        params.addParam('resize_mesh', False, "Resize the input mesh")
        params.addParam('off_diagonal', True, "Also test the off-diagonal Jacobian entries")
        params.addParam('mesh_size', 1, "Resize the input mesh")

        return params

    def __init__(self, *args, **kwargs):
        FileTester.__init__(self, *args, **kwargs)

    def getOutputFiles(self):
        # analizejacobian.py outputs files prefixed with the input file name
        return [self.specs['input']]

    def prepare(self, options):
        # We do not know what file(s) analizejacobian.py produces
        return

    # Check if numpy is available
    def checkRunnable(self, options):
        try:
            import numpy
            assert numpy  # silence pyflakes warning
            return True
        except Exception:
            self.addCaveats('skipped (no numpy)')
            return False

    def getCommand(self, options):
        specs = self.specs
        # Create the command line string to run
        command = os.path.join(os.path.dirname(__file__), '..', '..', 'mooseutils',
                               'analyzejacobian.py')

        # Check for built application
        if not options.dry_run and not os.path.exists(command):
            print('Application not found: ' + str(specs['executable']))
            sys.exit(1)

        mesh_options = ' -m %s' % options.method
        if specs['resize_mesh']:
            mesh_options += ' -r -s %d' % specs['mesh_size']

        if not specs['off_diagonal']:
            mesh_options += ' -D'

        command += mesh_options + ' ' + specs['input'] + ' -e ' + specs['executable'] + ' '
        if len(specs['cli_args']):
            command += '--cli-args "' + (' '.join(specs['cli_args']) + '"')

        return command

    def processResults(self, moose_dir, options, output):
        reason = ''
        specs = self.specs
        if specs.isValid('expect_out'):
            out_ok = util.checkOutputForPattern(output, specs['expect_out'])
            if (out_ok and self.exit_code != 0):
                reason = 'OUT FOUND BUT CRASH'
            elif (not out_ok):
                reason = 'NO EXPECTED OUT'
        if reason == '':
            if self.exit_code != 0:
                reason = 'CRASH'

        if reason != '':
            self.setStatus(self.fail, reason)

        return output
