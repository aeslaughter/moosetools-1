#!/usr/bin/env python3
#* This file is part of MOOSETOOLS repository
#* https://www.github.com/idaholab/moosetools
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moosetools/blob/main/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

import unittest
from unittest import mock
import subprocess
from moosetools import mooseutils


class Test(unittest.TestCase):
    @mock.patch('subprocess.call')
    def testRun(self, subproc):
        mooseutils.run_executable('command', '-arg', '-arg2')
        subproc.assert_called_with(['command', '-arg', '-arg2'], encoding='utf-8')

    @mock.patch('subprocess.call')
    def testRunMPI(self, subproc):
        mooseutils.run_executable('command', '-arg', '-arg2', mpi=2)
        subproc.assert_called_with(['mpiexec', '-n', '2', 'command', '-arg', '-arg2'],
                                   encoding='utf-8')

    @mock.patch('subprocess.call')
    def testRunSupressOutput(self, subproc):
        mooseutils.run_executable('command', '-arg', '-arg2', suppress_output=True)
        subproc.assert_called_with(['command', '-arg', '-arg2'],
                                   encoding='utf-8',
                                   stderr=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL)


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)
