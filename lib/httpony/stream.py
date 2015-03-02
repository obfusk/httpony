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

  def readchunks(self, size = DEFAULT_BUFSIZE, length = None):
    """chunk (of up to size bytes) iterator"""
    if length == None:
      while True:
        chunk = self.read(size)
        if not chunk: break
        yield chunk
    else:
      while length > 0:
        n = min(length, size); chunk = self.read(n); length -= n
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
    self.file = file
    super(IFileStream, self).__init__(*a, **k)

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
    self.file = file
    super(OFileStream, self).__init__(*a, **k)

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
    self.sock     = sock
    self.bufsize  = DEFAULT_BUFSIZE
    file          = sock.makefile("rb", bufsize)
    super(ISocketStream, self).__init__(file, *a, **k)

  def close(self):
    self.sock.shutdown(); self.sock.close()
    return super(ISocketStream, self).close()


class OSocketStream(OFileStream):

  """socket output stream"""

  def __init__(self, sock, bufsize = DEFAULT_BUFSIZE):
    self.sock     = sock
    self.bufsize  = DEFAULT_BUFSIZE
    file          = sock.makefile("wb", bufsize)
    super(OSocketStream, self).__init__(file, *a, **k)

  def close(self):
    self.sock.shutdown(); self.sock.close()
    return super(OSocketStream, self).close()


class IRequestStream(IFileStream):

  """SocketServer request handler input stream"""

  def __init__(self, handler):
    self.handler = handler; file = handler.rfile
    super(IRequestStream, self).__init__(file, *a, **k)


class ORequestStream(OFileStream):

  """SocketServer request handler output stream"""

  def __init__(self, handler):
    self.handler = handler; file = server.wfile
    super(ORequestStream, self).__init__(file, *a, **k)


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
