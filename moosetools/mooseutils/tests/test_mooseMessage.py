#!/usr/bin/env python3
#* This file is part of MOOSETOOLS repository
#* https://www.github.com/idaholab/moosetools
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moosetools/blob/main/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

import sys
import unittest
from io import StringIO
from unittest import mock
from moosetools.mooseutils import message


class TestMooseMessage(unittest.TestCase):
    """
    Tests the usage of the various messages functions in message package.
    """
    def testMooseMessageDefault(self):
        """
        Test the default message with a string and a number supplied.
        """
        with mock.patch('sys.stdout', new=StringIO()) as stdout:
            message.mooseMessage("The default message with a number", 1.0)
        output = stdout.getvalue()
        self.assertIn("The default message with a number 1.0", output)

    @unittest.skip('Breaks with current package')
    def testMooseMessageTraceback(self):
        """
        Test that the traceback argument is operational.
        """
        with mock.patch('sys.stdout', new=StringIO()) as stdout:
            with mock.patch('sys.stderr', new=StringIO()) as stderr:
                message.mooseMessage("A message", "with a traceback!", traceback=True)
        output = stdout.getvalue()
        err = stderr.getvalue()
        self.assertIn("A message with a traceback!", output)
        self.assertIn("message.mooseMessage", err)

    def testMooseMessageColor(self):
        """
        Test that the color flag is working.
        """
        with mock.patch('sys.stdout', new=StringIO()) as stdout:
            message.mooseMessage("This should be RED.", color='RED')
        output = stdout.getvalue()
        self.assertIn('\033[31m', output)

    def testMooseMessageDebugOn(self):
        """
        Test that the debug flag enables debug messages.
        """
        message.MOOSE_DEBUG_MODE = True
        with mock.patch('sys.stdout', new=StringIO()) as stdout:
            message.mooseMessage("You should see this!", debug=True)
        output = stdout.getvalue()
        self.assertIn("You should see this!", output)

    def testMooseMessageDebugOff(self):
        """
        Test that the debug flag enables debug messages.
        """
        message.MOOSE_DEBUG_MODE = False
        with mock.patch('sys.stdout', new=StringIO()) as stdout:
            message.mooseDebug("You should see this!", debug=True)
        output = stdout.getvalue()
        self.assertIn("You should see this!", output)

    @unittest.skip('Breaks with current package')
    def testMooseError(self):
        """
        Tests mooseError function.
        """
        with mock.patch('sys.stdout', new=StringIO()) as stdout:
            with mock.patch('sys.stderr', new=StringIO()) as stderr:
                message.mooseError("Don't do it!")
        output = stdout.getvalue()
        err = stderr.getvalue()
        self.assertIn('ERROR', output)
        self.assertIn("Don't do it!", output)
        self.assertIn("in mooseError", err)
        self.assertIn('\033[31m', output)

    def testMooseWarning(self):
        """
        Tests mooseWarning function.
        """
        with mock.patch('sys.stdout', new=StringIO()) as stdout:
            message.mooseWarning("Just a little warning")
        output = stdout.getvalue()
        self.assertIn('WARNING', output)
        self.assertIn("Just a little warning", output)
        self.assertIn('\033[33m', output)

    def testDebugMessageOn(self):
        """
        Test use of mooseDebug function, with debugging enabled.
        """
        message.MOOSE_DEBUG_MODE = True
        with mock.patch('sys.stdout', new=StringIO()) as stdout:
            message.mooseDebug("You should see this!")
        output = stdout.getvalue()
        self.assertIn("You should see this!", output)

    def testDebugMessageOff(self):
        """
        Test use of mooseDebug function, with debugging disabled.
        """
        message.MOOSE_DEBUG_MODE = False
        with mock.patch('sys.stdout', new=StringIO()) as stdout:
            message.mooseDebug("You should NOT see this!")
        output = stdout.getvalue()
        self.assertNotIn("You should NOT see this!", output)


if __name__ == '__main__':
    unittest.main(module=__name__, verbosity=2, buffer=True, exit=False)
