# --                                                            ; {{{1
#
# File        : httpony/stream.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-06
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

"""stream abstraction"""

import StringIO

CRLF            = "\r\n"
DEFAULT_BUFSIZE = 1024

class IStream(object):                                          # {{{1

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

  def split(self, n, bufsize = DEFAULT_BUFSIZE):
    """split stream at pos n"""
    t = IStreamTake(self, n, bufsize)
    d = IStreamDrop(self, t)
    return (t, d)

  def close(self):
    """ close stream"""
    raise NotImplementedError
                                                                # }}}1

class IStreamTake(IStream):                                     # {{{1

  """first part (n bytes) of split stream"""

  def __init__(self, parent, n, bufsize = DEFAULT_BUFSIZE, *a, **k):
    self.parent = parent; self.n = n; self.bufsize = bufsize
    self.buf = ""
    super(IStreamTake, self).__init__(*a, **k)

  def done(self):
    """has this part been read entirely?"""
    return self.n == 0

  def peek(self, size = None):
    """peek at first size bytes (read w/o consume)"""
    if size == -1   : size = self.n
    if size is None : size = self.bufsize
    m = min(size, self.n)
    if m > len(self.buf):
      self.buf += self.parent.read(m - len(self.buf))
    return self.buf[:m]

  def read(self, size = None):
    if size is None: size = self.n
    m = min(size, self.n); self.n -= m
    if m <= len(self.buf):
      buf = self.buf; self.buf = buf[m:]
      return buf[:m]
    else:
      buf = self.buf; self.buf = ""
      return buf + self.parent.read(m - len(buf))

  def readline(self):
    buf = ""
    while True:
      data = self.peek(self.bufsize)
      if data == "": break
      i = data.find("\n")
      if i != -1: return buf + self.read(i + 1)
      buf += self.read(self.bufsize)
    return buf
                                                                # }}}1

class IStreamDrop(IStream):                                     # {{{1

  """rest of split stream"""

  def __init__(self, parent, take, *a, **k):
    self.parent = parent; self.take = take
    super(IStreamDrop, self).__init__(*a, **k)

  def _force_take(self):
    if not self.take.done(): self.take.peek(-1)

  def read(self, size = None):
    self._force_take()
    return self.parent.read(size)

  def readline(self):
    self._force_take()
    return self.parent.readline()
                                                                # }}}1

class OStream(object):                                          # {{{1

  """output stream"""

  def __init__(self):
    pass

  def write(self, data):
    """write data to stream"""
    raise NotImplementedError

  def close(self):
    """ close stream"""
    raise NotImplementedError
                                                                # }}}1

class IFileStream(IStream):                                     # {{{1

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
                                                                # }}}1

class OFileStream(OStream):                                     # {{{1

  """file output stream"""

  def __init__(self, file, *a, **k):
    self.file = file
    super(OFileStream, self).__init__(*a, **k)

  def write(self, data):
    return self.file.write(data)

  def close(self):
    return self.file.close()
                                                                # }}}1

class IStringStream(IFileStream):                               # {{{1

  """string input stream"""

  def __init__(self, data, *a, **k):
    file = StringIO.StringIO(data)
    super(IStringStream, self).__init__(file, *a, **k)
                                                                # }}}1

class OStringStream(OFileStream):                               # {{{1

  """string output stream"""

  def __init__(self, *a, **k):
    file = StringIO.StringIO("")
    super(OStringStream, self).__init__(file, *a, **k)

  def getvalue(self):
    return self.file.getvalue()
                                                                # }}}1

class ISocketStream(IFileStream):                               # {{{1

  """socket input stream"""

  def __init__(self, sock, bufsize = DEFAULT_BUFSIZE):
    self.sock     = sock
    self.bufsize  = DEFAULT_BUFSIZE
    file          = sock.makefile("rb", bufsize)
    super(ISocketStream, self).__init__(file, *a, **k)

  def close(self):
    self.sock.shutdown(); self.sock.close()
    return super(ISocketStream, self).close()
                                                                # }}}1

class OSocketStream(OFileStream):                               # {{{1

  """socket output stream"""

  def __init__(self, sock, bufsize = DEFAULT_BUFSIZE):
    self.sock     = sock
    self.bufsize  = DEFAULT_BUFSIZE
    file          = sock.makefile("wb", bufsize)
    super(OSocketStream, self).__init__(file, *a, **k)

  def close(self):
    self.sock.shutdown(); self.sock.close()
    return super(OSocketStream, self).close()
                                                                # }}}1

class IRequestHandlerStream(IFileStream):                       # {{{1

  """SocketServer request handler input stream"""

  def __init__(self, handler, *a, **k):
    self.handler = handler; file = handler.rfile
    super(IRequestHandlerStream, self).__init__(file, *a, **k)
                                                                # }}}1

class ORequestHandlerStream(OFileStream):                       # {{{1

  """SocketServer request handler output stream"""

  def __init__(self, handler, *a, **k):
    self.handler = handler; file = handler.wfile
    super(ORequestHandlerStream, self).__init__(file, *a, **k)
                                                                # }}}1

def interact(istream, ostream, f):
  """map input stream to output stream using a generator function that
  returns chunks"""
  for chunk in f(istream):
    ostream.write(chunk)

def stripped_lines(lines):
  """wraps line iterator, strips trailing '\\r' and '\\n'"""
  return (line.rstrip(CRLF) for line in lines)

def unstripped_lines(lines):
  """wraps line iterator, adds trailing '\\r\\n'"""
  return (line + CRLF for line in lines)

# ...

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
