# --                                                            ; {{{1
#
# File        : httpony/http.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-05
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

from . import stream as S
from . import util as U
import collections
import urlparse

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

HTTP_DEFAULT_PORT = 80
HTTP_SCHEME       = "http"

HTTP_METHODS      = "OPTIONS GET HEAD POST PUT DELETE".split()

class URI(U.Immutable):                                         # {{{1

  """HTTP URI"""

  __slots__ = "scheme username password host port path \
               query fragment uri".split()

  def __init__(self, uri):
    if not uri.startswith(HTTP_SCHEME + "://"):
      uri = HTTP_SCHEME + "://" + uri
    u = urlparse.urlparse(uri)
    q = urlparse.parse_qs(u.query, True, True) if u.query else {}
    for k in q:
      if len(q[k]) == 1: q[k] = q[k][0]
    super(URI, self).__init__(
      scheme = u.scheme, username = u.username, password = u.password,
      host = u.hostname, port = u.port or HTTP_DEFAULT_PORT,
      path = u.path, query = q, fragment = u.fragment, uri = uri
    )

  @property
  def relative_uri(self):
    return self.uri[len(HTTP_SCHEME + "://"):]

  def __eq__(self, rhs):
    if isinstance(rhs, str):
      return self.uri == rhs or self.relative_uri == rhs
    return super(URI, self).__eq__(rhs)

  # ...
                                                                # }}}1

class Message(U.Immutable):                                     # {{{1

  """HTTP request or response message (base class)"""

  def __init__(self, **kw):
    super(Message, self).__init__(self._defaults(), **kw)
    if not isinstance(self.headers, U.idict):
      self._Immutable___set("headers", U.idict(self.headers))
    if isinstance(self.body, str):
      self._Immutable___set("body", (self.body,))
    elif isinstance(self.body, S.IStream):
      self._Immutable___set("body", self.body.readchunks())

  def unparse(self):
    """request/response as string"""
    return "".join(self.unparse_chunked())

  def unparse_chunked(self):
    """iterate over chunks of request/response as string"""
    start_line = self.unparse_start_line()
    headers = ["{}: {}".format(k, v)
               for (k,v) in self.headers.iteritems()]
    yield "".join(S.unstripped_lines([start_line] + headers + [""]))
    for chunk in self.body: yield chunk

  def force_body(self):
    """force body into a 1-tuple and return its only element"""
    if not (isinstance(self.body, tuple) and len(self.body) == 1):
      self._Immutable___set("body", ("".join(self.body),))
    return self.body[0]
                                                                # }}}1

class Request(Message):                                         # {{{1

  """HTTP request"""

  __slots__ = "method uri version headers body env".split()

  def __init__(self, data = None, **kw):
    if data is not None:
      if len(kw):
        raise TypeError("arguments must either be " +
                        "data or keywords, not both")
      elif isinstance(data, collections.Mapping):
        kw = data
      else:
        raise TypeError("data argument must be a mapping")
    super(Request, self).__init__(**kw)
    if not isinstance(self.uri, URI):
      self._Immutable___set("uri", URI(self.uri))

  def unparse_start_line(self):
    return "{} {} {}".format(self.method, self.uri.relative_uri,
                             self.version)

  def _defaults(self):
    return dict(
      method = "GET", uri = "/", version = "HTTP/1.1",
      headers = U.idict(), body = "", env = {}
    )
                                                                # }}}1

class Response(Message):                                        # {{{1

  """HTTP response"""

  __slots__ = "version status reason headers body".split()

  def __init__(self, data = None, **kw):
    if data is not None:
      if len(kw):
        raise TypeError("arguments must either be "
                        "data or keywords, not both")
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
        raise TypeError("data argument must be a " +
                        "mapping, 3-tuple, int, str, or iterable")
    super(Response, self).__init__(**kw)
    if "reason" not in kw:
      self._Immutable___set("reason", HTTP_STATUS_CODES[self.status])

  def unparse_start_line(self):
    return "{} {} {}".format(self.version, self.status, self.reason)

  def _defaults(self):
    return dict(
      version = "HTTP/1.1", status = 200, headers = U.idict(),
      body = ""
    )
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
      si.close(); return
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

def force_bodies(xs):
  """force bodies in message stream"""
  for msg in xs:
    msg.force_body(); yield msg

# ...

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
