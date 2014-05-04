import sys

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

class CapturedStream(object):
    def __init__(self, stream_name):
        self.stream_name = stream_name
        self.original_stream = getattr(sys, stream_name)
        self.pseudo_stream = StringIO()

    def __enter__(self):
        setattr(sys, self.stream_name, self.pseudo_stream)
        return self.pseudo_stream

    def __exit__(self, *unused):
        setattr(sys, self.stream_name, self.original_stream)
