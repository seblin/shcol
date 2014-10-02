# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

import os
import shcol
import subprocess
import unittest

SHCOL = os.path.join('bin', 'shcol')

class ScriptTest(unittest.TestCase):
    def check_output(self, args):
        return subprocess.check_output(args).decode('utf-8')

    def test_script_args(self):
        args = ['spam', 'ham', 'eggs']
        result = self.check_output([SHCOL, '-w80'] + args)
        expected = shcol.columnize(args, line_width=80) + '\n'
        self.assertEqual(result, expected)

    def test_script_help(self):
        parser = shcol.cli.ArgumentParser('shcol', shcol.__version__)
        result = self.check_output([SHCOL, '--help'])
        self.assertEqual(result, parser.format_help())
