# -*- coding: utf-8 -*-
# Copyright (c) 2013-2016, Sebastian Linke

# Released under the Simplified BSD license
# (see LICENSE file for details).

import os
import shcol
import subprocess
import unittest

class ScriptTest(unittest.TestCase):
    def setUp(self):
        self.starter = shcol.config.STARTER
        if not os.path.isfile(self.starter):
            self.starter = os.path.join('..', self.starter)

    def check_output(self, args):
        return subprocess.check_output(args, universal_newlines=True)

    def test_script_args(self):
        args = ['spam', 'ham', 'eggs']
        result = self.check_output([self.starter, '-w80'] + args)
        expected = shcol.columnize(args, line_width=80) + '\n'
        self.assertEqual(result, expected)

    def test_script_help(self):
        parser = shcol.cli.ArgumentParser('shcol', shcol.__version__)
        result = self.check_output([self.starter, '--help'])
        self.assertEqual(result, parser.format_help())
