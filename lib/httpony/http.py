# --                                                            ; {{{1
#
# File        : httpony/http.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-04-02
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

"""HTTP URIs, requests, responses, streams"""

from . import stream as S
from . import util as U
from .util import BY, STR
from functools import reduce
import collections
import operator

try:
  import urlparse                 # python2
except ImportError:
  import urllib.parse as urlparse # python3

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

HTTP_DEFAULT_PORT   = 80
HTTPS_DEFAULT_PORT  = 443

HTTP_SCHEME         = "http"
HTTPS_SCHEME        = "https"

HTTP_METHODS        = "OPTIONS GET HEAD POST PUT DELETE".split()

# TODO
class Error(RuntimeError):
  pass

class URI(U.Immutable):                                         # {{{1

  """HTTP(S) URI"""

  __slots__ = "scheme username password host port path \
               query query_params fragment".split()

  def __init__(self, uri):
    if not (uri.startswith(HTTP_SCHEME  + "://") or \
            uri.startswith(HTTPS_SCHEME + "://")):
      uri = HTTP_SCHEME + "://" + uri
    u = urlparse.urlparse(uri)
    q = urlparse.parse_qs(u.query, True, True) if u.query else {}
    for k in q:
      if len(q[k]) == 1: q[k] = q[k][0]
    port = u.port
    if not port:
      port = HTTPS_DEFAULT_PORT if u.scheme == HTTPS_SCHEME \
                                else HTTP_DEFAULT_PORT
    super(URI, self).__init__(
      scheme = u.scheme, username = u.username,
      password = u.password, host = u.hostname or "",
      port = port, path = u.path or "/", query = u.query,
      query_params = q, fragment = u.fragment
    )

  @property
  def uri_with_fragment(self):
    s = self.uri
    if self.fragment: s += "#" + self.fragment
    return s

  @property
  def uri(self):
    return self.scheme + "://" + self.schemeless_uri

  @property
  def schemeless_uri(self):
    return self.username_and_password + self.host_and_port + \
           self.relative_uri

  @property
  def relative_uri(self):
    return self.path + self.query_string

  @property
  def username_and_password(self):
    if self.password:
      s = ":" + self.password + "@"
      if self.username: s = self.username + s
    elif self.username:
      s = self.username + "@"
    else:
      s = ""
    return s

  @property
  def host_and_port(self):
    s = self.host or ""
    if self.non_default_port: s += ":" + str(self.port)
    return s

  @property
  def non_default_port(self):
    if self.port and ((self.scheme == HTTP_SCHEME and
                       self.port != HTTP_DEFAULT_PORT) or
                      (self.scheme == HTTPS_SCHEME and
                       self.port != HTTPS_DEFAULT_PORT)):
      return self.port
    else:
      return None

  @property
  def query_string(self):
    return "?" + self.query if self.query else ""

  def with_scheme(self, scheme):
    """with other scheme"""
    return type(self)(scheme + "://" + self.schemeless_uri)

  def with_host_and_port(self, host_and_port):
    """with other host:port"""
    return type(self)(self.scheme + "://" +
                      self.username_and_password + host_and_port +
                      self.relative_uri)

  def with_path(self, path):
    """with other path"""
    if not path.startswith("/"): path = "/" + path
    return type(self)(self.scheme + "://" +
                      self.username_and_password +
                      self.host_and_port + path + self.query_string)

  def __eq__(self, rhs):
    if isinstance(rhs, str  ): rhs = type(self)(rhs)
    if isinstance(rhs, bytes): rhs = type(self)(STR(rhs))
    return super(URI, self).__eq__(rhs)
                                                                # }}}1

class Message(U.Immutable):                                     # {{{1

  """HTTP request or response message (base class)"""

  def __init__(self, **kw):
    super(Message, self).__init__(self._defaults(), **kw)
    self._Immutable___set("_content_length", None)
    if not isinstance(self.headers, U.idict):
      self._Immutable___set("headers", U.idict(self.headers))
    if isinstance(self.body, str):
      self._Immutable___set("body", (BY(self.body),))
    elif isinstance(self.body, bytes):
      self._Immutable___set("body", (self.body,))
    elif isinstance(self.body, S.IStream):
      if self.body.length() is not None:
        self._Immutable___set("_content_length", self.body.length())
      self._Immutable___set("body", self.body.readchunks())

  def unparse(self, with_body = True):
    """request/response as string"""
    return b"".join(self.unparse_chunked(with_body))

  def unparse_chunked(self, with_body = True):
    """iterate over chunks of request/response as string"""
    if not isinstance(self.body, collections.Sized):
      self.headers["Transfer-Encoding"] = "chunked"
      chunked = True
    else:
      if self._content_length is None:
        self._Immutable___set(
          "_content_length",
          reduce(operator.add, map(len, self.body))
        )
      self.headers["Content-Length"] = self._content_length
      chunked = False
    start_line = BY(self.unparse_start_line())
    headers = [BY("{}: {}".format(k, v))
               for (k,v) in U.iteritems(self.headers)]
    yield b"".join(line + S.CRLFb
                   for line in [start_line] + headers + [b""])
    if not with_body:
      pass
    elif chunked:
      for chunk in (BY(c) for c in self.body):
        yield BY(hex(len(chunk))[2:]) + S.CRLFb + chunk + S.CRLFb
      yield b"0" + S.CRLFb + S.CRLFb
    else:
      for chunk in self.body: yield chunk

  @property
  def force_body(self):
    """force body into a 1-tuple and return its only element"""
    if not (isinstance(self.body, tuple) and len(self.body) == 1):
      self._Immutable___set("body",
                            (b"".join(BY(c) for c in self.body),))
    return self.body[0]
                                                                # }}}1

class Request(Message):                                         # {{{1

  """HTTP request"""

  __slots__ = "method uri version headers body env " \
              "_content_length".split()

  def __init__(self, data = None, **kw):
    if data is not None:
      if isinstance(data, collections.Mapping):
        kw = dict(data, **kw)
      else:
        raise TypeError("data argument must be a mapping")
    super(Request, self).__init__(**kw)
    if not isinstance(self.uri, URI):
      self._Immutable___set("uri", URI(self.uri))
    if not self.uri.host and "Host" in self.headers:
      self._Immutable___set(
        "uri", self.uri.with_host_and_port(self.headers["Host"])
      )
    if "scheme" in self.env:
      self._Immutable___set("uri",
                            self.uri.with_scheme(self.env["scheme"]))

  # TODO
  def params(self):
    """query_params + context_params"""
    params = self.uri.query_params.copy()
    params.update(self.env.get("context_params", {}))
    return params

  def update_env(self, env):
    """update self.env w/ env"""
    self.env.update(env)

  def with_uri(self, uri):
    """with other uri"""
    return self.copy(uri = uri)

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

  __slots__ = "version status reason headers body " \
              "_content_length".split()

  def __init__(self, data = None, **kw):
    if data is not None:
      if isinstance(data, collections.Mapping):
        kw = dict(data, **kw)
      elif len(kw):
        raise TypeError("arguments must either be "
                        "data or keywords, not both")
      elif isinstance(data, tuple):
        if len(data) == 2:
          status, body = data
          kw = dict(status = status, body = body)
        elif len(data) == 3:
          status, headers, body = data
          kw = dict(status = status, headers = headers, body = body)
        else:
          raise TypeError("tuple data argument must have "
                          "either 2 or 3 elements")
      elif isinstance(data, int):
        kw = dict(status = data)
      elif isinstance(data, str) or isinstance(data, bytes) or \
           isinstance(data, collections.Iterable):
        kw = dict(body = data)
      else:
        raise TypeError("data argument must be a mapping, "
                        "tuple, int, str, bytes, or iterable")
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

class _SIWrapper(object):
  def __init__(self, si): self.si = si
  def readline(self): return self.si.readline()

# NB: si is probably a _SIWrapper; only use .readline()
def generic_messages(si):                                       # {{{1
  """iterate over stream of HTTP messages (requests or responses)"""
  while True:
    headers = U.idict()
    while True:
      start_line = STR(si.readline())
      if start_line == "": return
      if start_line != S.CRLF: break
    while True:
      line = STR(si.readline())
      if line == "": return
      if line == S.CRLF: break
      k, v = line.split(":", 1); headers[k] = v.strip()
    yield dict(
      start_line = start_line.rstrip(S.CRLF), headers = headers,
      body = si
    )
                                                                # }}}1

# TODO: extensions, trailer
def http_chunked_chunks(si):                                    # {{{1
  while True:
    n = int(STR(si.readline()), 16)
    if n == 0: break
    yield si.split(n)[0].read()
    si.readline()
  si.readline()
                                                                # }}}1

def split_body(si, msg, bufsize):                               # {{{1
  """split stream into body and rest"""
  te = msg["headers"].get("Transfer-Encoding", "")
  cl = msg["headers"].get("Content-Length", 0)
  if te.lower() == "chunked":
    return si.splitchunked(http_chunked_chunks, bufsize)
  else:
    return si.split(int(cl), bufsize)
                                                                # }}}1

def requests(si, bufsize = S.DEFAULT_BUFSIZE):                  # {{{1
  """iterate over HTTP requests"""
  si_ = _SIWrapper(si)
  for msg in generic_messages(si_):
    method, uri, version = msg["start_line"].split(" ")
    co = msg["headers"].get("Connection", "keep-alive").lower()
    body, si_.si = split_body(si_.si, msg, bufsize)
    yield Request(
      method = method, uri = uri, version = version,
      headers = msg["headers"], body = body
    )
    if co == "close":
      si_.si.close(); return
                                                                # }}}1

def responses(si, bufsize = S.DEFAULT_BUFSIZE):                 # {{{1
  """iterate over HTTP responses"""
  si_ = _SIWrapper(si)
  for msg in generic_messages(si_):
    version, status, reason = msg["start_line"].split(" ", 2)
    body, si_.si = split_body(si_.si, msg, bufsize)
    yield Response(
      version = version, status = int(status), reason = reason,
      headers = msg["headers"], body = body
    )
                                                                # }}}1

def force_bodies(xs):
  """force bodies in message stream"""
  for msg in xs:
    msg.force_body; yield msg

def request(x):
  """make a Request (if x is not already one)"""
  if isinstance(x, Request): return x
  return Request(x)

def response(x):
  """make a Response (if x is not already one)"""
  if isinstance(x, Response): return x
  return Response(x)

# ...

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
