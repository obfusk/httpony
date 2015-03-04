# --                                                            ; {{{1
#
# File        : httpony/http.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-04
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

from . import stream as S
from . import util as U
import collections

HTTP_STATUS_CODES = {                                           # {{{1
  100 : "Continue",
  101 : "Switching Protocols",
  200 : "OK",
  201 : "Created",
  202 : "Accepted",
  203 : "Non-Authoritative Information",
  204 : "No Content",
  205 : "Reset Content",
  206 : "Partial Content",
  300 : "Multiple Choices",
  301 : "Moved Permanently",
  302 : "Found",
  303 : "See Other",
  304 : "Not Modified",
  305 : "Use Proxy",
  307 : "Temporary Redirect",
  400 : "Bad Request",
  401 : "Unauthorized",
  402 : "Payment Required",
  403 : "Forbidden",
  404 : "Not Found",
  405 : "Method Not Allowed",
  406 : "Not Acceptable",
  407 : "Proxy Authentication Required",
  408 : "Request Timeout",
  409 : "Conflict",
  410 : "Gone",
  411 : "Length Required",
  412 : "Precondition Failed",
  413 : "Request Entity Too Large",
  414 : "Request-URI Too Long",
  415 : "Unsupported Media Type",
  416 : "Requested Range Not Satisfiable",
  417 : "Expectation Failed",
  500 : "Internal Server Error",
  501 : "Not Implemented",
  502 : "Bad Gateway",
  503 : "Service Unavailable",
  504 : "Gateway Timeout",
  505 : "HTTP Version Not Supported"
}                                                               # }}}1

# TODO
class Message(object):                                          # {{{1

  """message (base class)"""

  __slots__ = []

  def __init__(self, **kw):
    x = self._defaults(); x.update(kw)
    for k in self.__slots__:
      if k in x:
        super(Message, self).__setattr__(k, x[k]); del x[k]
    if len(x):
      raise TypeError("unknown keys: {}".format("".join(x.keys())))

  # private!
  def _set(self, k, v):
    super(Message, self).__setattr__(k, v)

  def __setattr__(self, k, v):
    raise AttributeError(
      "'{}' object attribute '{}' is read-only".format(
        self.__class__.__name__, k
      )
    )

  def dict(self):
    return dict((k, self.__getattribute__(k)) for k in self.__slots__)

  def __eq__(self, rhs):
    if type(self) is not type(rhs):
      return False
    for k in self.__slots__:
      if self.__getattribute__(k) != rhs.__getattribute__(k):
        return False
    return True

  def __repr__(self):
    return '{}({})'.format(self.__class__.__name__, repr(self.dict()))
                                                                # }}}1

# TODO
class Request(Message):                                         # {{{1

  """HTTP request"""

  __slots__ = "method uri version headers body env".split()

  def __init__(self, data = None, **kw):
    if data != None:
      if len(kw):
        raise TypeError(
          "arguments must either be data or keywords, not both"
        )
      elif isinstance(data, collections.Mapping):
        kw = data
      else:
        raise TypeError("data argument must be a mapping")
    super(Request, self).__init__(**kw)
    if not isinstance(self.headers, U.idict):
      self._set("headers", U.idict(self.headers))

  def _defaults(self):
    return dict(
      method = "GET", uri = "/", version = "HTTP/1.1",
      headers = U.idict(), body = "", env = {}
    )

  # ...
                                                                # }}}1

# TODO
class Response(Message):                                        # {{{1

  """HTTP response"""

  __slots__ = "version status reason headers body".split()

  def __init__(self, data = None, **kw):
    if data != None:
      if len(kw):
        raise TypeError(
          "arguments must either be data or keywords, not both"
        )
      elif isinstance(data, collections.Mapping):
        kw = data
      elif isinstance(data, tuple):
        status, headers, body = data
        kw = dict(status = status, headers = headers, body = body)
      elif isinstance(data, int):
        kw = dict(status = data)
      elif isinstance(data, str) or \
           isinstance(data, collections.Iterable):
        kw = dict(body = data)
      else:
        raise TypeError(
          "data argument must be a " +
          "mapping, 3-tuple, int, str, or iterable"
        )
    super(Response, self).__init__(**kw)
    if "reason" not in kw:
      self._set("reason", HTTP_STATUS_CODES[self.status])
    if not isinstance(self.headers, U.idict):
      self._set("headers", U.idict(self.headers))
    if isinstance(self.body, str):
      self._set("body", (x for x in [self.body]))
    elif isinstance(self.body, S.IStream):
      self._set("body", self.body.readchunks())

  def _defaults(self):
    return dict(
      version = "HTTP/1.1", status = 200, headers = U.idict(),
      body = ""
    )

  # ...
                                                                # }}}1

def generic_messages(si):                                       # {{{1
  """iterate over stream of HTTP messages (requests or responses)"""
  while True:
    headers = U.idict()
    while True:
      start_line = si.readline()
      if start_line == "": return
      if start_line != S.CRLF: break
    while True:
      line = si.readline()
      if line == "": return
      if line == S.CRLF: break
      k, v = line.split(":", 1); headers[k] = v.strip()
    yield dict(
      start_line = start_line.rstrip(S.CRLF), headers = headers,
      body = si
    )
                                                                # }}}1

def split_body(msg, bufsize):
  """split stream into body and rest"""
  cl = int(msg["headers"].get("content-length", 0))
  return msg["body"].split(cl, bufsize)

def requests(si, bufsize = S.DEFAULT_BUFSIZE):                  # {{{1
  """iterate over HTTP requests"""
  for msg in generic_messages(si):
    method, uri, version = msg["start_line"].split(" ")
    co = msg["headers"].get("connection", "keep-alive").lower()
    body, si = split_body(msg, bufsize)
    yield Request(
      method = method, uri = uri, version = version,
      headers = msg["headers"], body = body
    )
    if co == "close":
      si.close()
      return
                                                                # }}}1

def responses(si, bufsize = S.DEFAULT_BUFSIZE):                 # {{{1
  """iterate over HTTP responses"""
  for msg in generic_messages(si):
    version, status, reason = msg["start_line"].split(" ", 2)
    body, si = split_body(msg, bufsize)
    yield Response(
      version = version, status = int(status), reason = reason,
      headers = msg["headers"], body = body
    )
                                                                # }}}1

# TODO
def evaluate_bodies(xs):
  """evaluate bodies in message stream"""
  for msg in xs:
    m = msg.dict(); m["body"] = "".join(m["body"])
    yield msg.__class__(m)

# ...

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
