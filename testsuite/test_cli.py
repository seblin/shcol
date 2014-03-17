import shcol
import sys
import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

class StdStreamRedirector(object):
    def __init__(self, name, dest):
        self.name = name
        self.dest = dest
        self.orig = getattr(sys, name)

    def __enter__(self):
        setattr(sys, self.name, self.dest)

    def __exit__(self, *unused):
        setattr(sys, self.name, self.orig)

class ArgumentParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = shcol.cli.ArgumentParser('shcol', shcol.__version__)

    def _check_output(self, args, expected, stream_name='stdout'):
        output = StringIO()
        with StdStreamRedirector(stream_name, output):
            try:
                self.parser.parse_args(args)
            except SystemExit:
                result = output.getvalue().rstrip('\n')
                self.assertEqual(result, expected)

    def test_version(self):
        expected = '{} {}'.format('shcol', shcol.__version__)
        for option in ('-v', '--version'):
            self._check_output(['shcol', option], expected, 'stderr')
