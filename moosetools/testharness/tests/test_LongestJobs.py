#* This file is part of MOOSETOOLS repository
#* https://www.github.com/idaholab/moosetools
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moosetools/blob/main/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

import subprocess
from TestHarnessTestCase import TestHarnessTestCase


class TestHarnessTester(TestHarnessTestCase):
    def testLongestJobs(self):
        """
        Test for --longest-jobs in the TestHarness with 2 passing jobs, 1 failing job, and 1 skipped job.
        """
        with self.assertRaises(subprocess.CalledProcessError) as cm:
            self.runTests('-i', 'longest_jobs', '--longest-jobs', '4')

        output = cm.exception.output.decode('utf-8')

        self.assertIn('4 longest running jobs', output)
        self.assertRegex(output, r'longest running jobs(?s).*run_1')
        self.assertRegex(output, r'longest running jobs(?s).*run_2')
        self.assertRegex(output, r'longest running jobs(?s).*run_fail')
        self.assertNotRegex(output, r'longest running jobs(?s).*run_skip')

    def testLongestJobsNoneCompleted(self):
        """
        Test for --longest-jobs in the TestHarness with no jobs ran.
        """
        output = self.runTests('-i', 'longest_jobs', '--re', 'foo', '--longest-jobs',
                               '100').decode('utf-8')

        self.assertIn('100 longest running jobs', output)
        self.assertNotRegex(output, r'longest running jobs(?s).*<No jobs were completed>')
