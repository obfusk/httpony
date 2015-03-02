# --                                                            ; {{{1
#
# File        : httpony/stream.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-01
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

import StringIO

CRLF            = "\r\n"
DEFAULT_BUFSIZE = 1024

class IStream(object):

  """input stream"""

  def __init__(self):
    pass

  def read(self, size = None):
    """read up to size bytes from stream"""
    raise NotImplementedError

  def readline(self):
    """read line"""
    raise NotImplementedError

  def readlines(self):
    """lines iterator"""
    while True:
      line = self.readline()
      if not line: break
      yield line

  def __iter__(self):
    return self.readlines()

  def readchunks(self, size = DEFAULT_BUFSIZE):
    """chunk (of up to size bytes) iterator"""
    while True:
      chunk = self.read(size)
      if not chunk: break
      yield chunk

  def close(self):
    """ close stream"""
    raise NotImplementedError


class OStream(object):

  """output stream"""

  def __init__(self):
    pass

  def write(self, data):
    """write data to stream"""
    raise NotImplementedError

  def close(self):
    """ close stream"""
    raise NotImplementedError


class IFileStream(IStream):

  """file input stream"""

  def __init__(self, file, *a, **k):
    super(IFileStream, self).__init__(*a, **k)
    self.file = file

  def read(self, size = None):
    return self.file.read(size)

  def readline(self):
    return self.file.readline()

  def readlines(self):
    return self.file.__iter__()

  def close(self):
    return self.file.close()


class OFileStream(OStream):

  """file output stream"""

  def __init__(self, file, *a, **k):
    super(OFileStream, self).__init__(*a, **k)
    self.file = file

  def write(self, data):
    return self.file.write(data)

  def close(self):
    return self.file.close()


class IStringStream(IFileStream):

  """string input stream"""

  def __init__(self, data, *a, **k):
    file = StringIO.StringIO(data)
    super(IStringStream, self).__init__(file, *a, **k)


class OStringStream(OFileStream):

  """string output stream"""

  def __init__(self, *a, **k):
    file = StringIO.StringIO("")
    super(OStringStream, self).__init__(file, *a, **k)

  def getvalue(self):
    return self.file.getvalue()


class ISocketStream(IFileStream):

  """socket input stream"""

  def __init__(self, sock, bufsize = DEFAULT_BUFSIZE):
    self.bufsize = DEFAULT_BUFSIZE
    file = sock.makefile("rb", bufsize)
    super(ISocketStream, self).__init__(file, *a, **k)


class OSocketStream(OFileStream):

  """socket output stream"""

  def __init__(self, sock, bufsize = DEFAULT_BUFSIZE):
    self.bufsize = DEFAULT_BUFSIZE
    file = sock.makefile("wb", bufsize)
    super(OSocketStream, self).__init__(file, *a, **k)


class ISocketServerStream(IFileStream):

  """SocketServer input stream"""

  def __init__(self, server):
    file = server.rfile
    super(ISocketServerStream, self).__init__(file, *a, **k)


class OSocketServerStream(OFileStream):

  """SocketServer output stream"""

  def __init__(self, server):
    file = server.wfile
    super(OSocketServerStream, self).__init__(file, *a, **k)


def interact(istream, ostream, f):
  """map input stream to output stream using a generator function that
  returns chunks"""
  for chunk in f(istream):
    ostream.write(chunk)

def stripped_lines(x):
  """wraps line iterator, strips trailing '\\r' and '\\n'"""
  for line in x:
    yield line.rstrip("\r\n")

# ...

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
