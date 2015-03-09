# --                                                            ; {{{1
#
# File        : httpony/stream.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-09
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

"""stream abstraction"""

import os
import StringIO

CRLF            = "\r\n"
DEFAULT_BUFSIZE = 1024

class IStream(object):                                          # {{{1

  """input stream"""

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

  def splitchunked(self, chunks, bufsize = DEFAULT_BUFSIZE):
    """split stream after chunks"""
    t = IStreamTakeChunks(chunks(self), bufsize)
    d = IStreamDrop(self, t)
    return (t, d)

  def close(self):
    """close stream"""
    raise NotImplementedError

  def length(self):
    """length (int or None if unknown)"""
    return None
                                                                # }}}1

class _IStreamTakeBase(IStream):                                # {{{1

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

class IStreamTake(_IStreamTakeBase):                            # {{{1

  """first part (n bytes) of split stream"""

  def __init__(self, parent, n, bufsize = DEFAULT_BUFSIZE):
    self.parent = parent; self.n = n; self.bufsize = bufsize
    self.buf = ""

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
                                                                # }}}1

class IStreamTakeChunks(_IStreamTakeBase):                      # {{{1

  """first part of splitchunked stream"""

  def __init__(self, chunks, bufsize = DEFAULT_BUFSIZE):
    self.chunks = chunks; self.bufsize = bufsize; self._done = False
    self.buf = ""

  def done(self):
    """has this part been read entirely?"""
    return self._done

  def peek(self, size = None):
    """peek at first size bytes (read w/o consume)"""
    if size == -1:
      self.buf += "".join(self.chunks)
      return self.buf
    if size is None: size = self.bufsize
    while size > len(self.buf):
      x = next(self.chunks, None)
      if x is None: break
      self.buf += x
    return self.buf[:size]

  def read(self, size = None):
    if size is None:
      buf = self.buf + "".join(self.chunks); self.buf = ""
      self._done = True
      return buf
    while size > len(self.buf):
      x = next(self.chunks, None)
      if x is None:
        self._done = True; break
      self.buf += x
    buf = self.buf; self.buf = buf[size:]
    return buf[:size]
                                                                # }}}1

class IStreamDrop(IStream):                                     # {{{1

  """rest of split stream"""

  def __init__(self, parent, take):
    self.parent = parent; self.take = take

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

  def write(self, data):
    """write data to stream"""
    raise NotImplementedError

  def close(self):
    """close stream"""
    raise NotImplementedError

  def flush(self):
    """flush stream"""
    raise NotImplementedError
                                                                # }}}1

class IFileStream(IStream):                                     # {{{1

  """file input stream"""

  def __init__(self, file, length = None):
    self.file = file; self._length = length

  def read(self, size = None):
    return self.file.read(size)

  def readline(self):
    return self.file.readline()

  def readlines(self):
    return self.file.__iter__()

  def close(self):
    return self.file.close()

  def length(self):
    return self._length
                                                                # }}}1

class OFileStream(OStream):                                     # {{{1

  """file output stream"""

  def __init__(self, file):
    self.file = file

  def write(self, data):
    return self.file.write(data)

  def close(self):
    return self.file.close()

  def flush(self):
    return self.file.flush()
                                                                # }}}1

class IStringStream(IFileStream):                               # {{{1

  """string input stream"""

  def __init__(self, data):
    super(IStringStream, self).__init__(StringIO.StringIO(data))
                                                                # }}}1

class OStringStream(OFileStream):                               # {{{1

  """string output stream"""

  def __init__(self):
    super(OStringStream, self).__init__(StringIO.StringIO())

  def getvalue(self):
    return self.file.getvalue()
                                                                # }}}1

class ISocketStream(IFileStream):                               # {{{1

  """socket input stream"""

  def __init__(self, sock, bufsize = DEFAULT_BUFSIZE):
    self.sock     = sock
    self.bufsize  = DEFAULT_BUFSIZE
    file          = sock.makefile("rb", bufsize)
    super(ISocketStream, self).__init__(file)

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
    super(OSocketStream, self).__init__(file)

  def close(self):
    self.sock.shutdown(); self.sock.close()
    return super(OSocketStream, self).close()
                                                                # }}}1

class IRequestHandlerStream(IFileStream):                       # {{{1

  """SocketServer request handler input stream"""

  def __init__(self, handler):
    self.handler = handler
    super(IRequestHandlerStream, self).__init__(handler.rfile)
                                                                # }}}1

class ORequestHandlerStream(OFileStream):                       # {{{1

  """SocketServer request handler output stream"""

  def __init__(self, handler):
    self.handler = handler
    super(ORequestHandlerStream, self).__init__(handler.wfile)
                                                                # }}}1

def ifile_stream(name):
  """file stream (w/ size)"""
  return IFileStream(open(name, "r"), os.stat(name).st_size)

def interact(istream, ostream, f):
  """map input stream to output stream using a generator function that
  returns chunks"""
  for chunk in f(istream):
    if chunk is None:
      ostream.flush()
    else:
      ostream.write(chunk)

def stripped_lines(lines):
  """wraps line iterator, strips trailing '\\r' and '\\n'"""
  return (line.rstrip(CRLF) for line in lines)

def unstripped_lines(lines):
  """wraps line iterator, adds trailing '\\r\\n'"""
  return (line + CRLF for line in lines)

# ...

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
