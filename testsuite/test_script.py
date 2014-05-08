import os
import shcol
import subprocess
import unittest

SHCOL = os.path.join('bin', 'shcol')

class ScriptTest(unittest.TestCase):
    def test_script_args(self):
        args = ['spam', 'ham', 'eggs']
        result = subprocess.check_output([SHCOL, '-w80'] + args)
        expected = shcol.columnize(args, max_line_width=80) + '\n'
        self.assertEqual(result, expected)

    def test_script_help(self):
        parser = shcol.cli.ArgumentParser('shcol', shcol.__version__)
        result = subprocess.check_output([SHCOL, '--help'])
        self.assertEqual(result, parser.format_help())
