# -*- coding: utf-8 -*-
# Copyright (c) 2013-2015, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

import os
import shcol
import subprocess
import sys
import unittest

class ScriptTest(unittest.TestCase):
    def setUp(self):
        self.shcol_cmd = os.path.join('bin', 'shcol')
        if not os.path.isfile(self.shcol_cmd):
            self.shcol_cmd = os.path.join('..', self.shcol_cmd)
        if sys.platform.startswith('win'):
            self.shcol_cmd += '.bat'

    def check_output(self, args):
        return subprocess.check_output(args, universal_newlines=True)

    def test_script_args(self):
        args = ['spam', 'ham', 'eggs']
        result = self.check_output([self.shcol_cmd, '-w80'] + args)
        expected = shcol.columnize(args, line_width=80) + '\n'
        self.assertEqual(result, expected)

    def test_script_help(self):
        parser = shcol.cli.ArgumentParser('shcol', shcol.__version__)
        result = self.check_output([self.shcol_cmd, '--help'])
        self.assertEqual(result, parser.format_help())
