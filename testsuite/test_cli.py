import shcol
import sys
import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

class ArgumentParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = shcol.cli.ArgumentParser('shcol', shcol.__version__)

    def _get_stderr_output(self, args):
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        result = ''
        try:
            self.parser.parse_args(args)
        except SystemExit:
            result = sys.stderr.getvalue().rstrip('\n')
        finally:
            sys.stderr = old_stderr
        return result

    def test_version(self):
        expected = '{} {}'.format('shcol', shcol.__version__)
        for option in ('-v', '--version'):
            result = self._get_stderr_output(['shcol', option])
            self.assertEqual(result, expected)

    def test_spacing(self):
        invalid_spacings = ['-42', '-1', '1.0', 'x']
        for spacing in invalid_spacings:
            error = self._get_stderr_output(['shcol', '--spacing', spacing])
            self.assertTrue(error)
        valid_spacings = ['0', '2', '100']
        for spacing in valid_spacings:
            args = self.parser.parse_args(['shcol', '--spacing', spacing])
            self.assertEqual(args.spacing, int(spacing))
