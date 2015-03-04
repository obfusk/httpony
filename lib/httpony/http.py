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
class Request(object):                                          # {{{1

  """..."""

  __slots__ = "method uri version headers body env".split()

  def __init__(self, **kw):
    pass
                                                                # }}}1

# TODO
class Response(object):                                         # {{{1

  """..."""

  __slots__ = "version status reason headers body".split()

  def __init__(self, **kw):
    pass
                                                                # }}}1

# TODO
def generic_messages(si):                                       # {{{1
  """..."""
  while True:
    headers = {}
    while True:
      start_line = si.readline()
      if start_line == "": return
      if start_line != S.CRLF: break
    while True:
      line = si.readline()
      if line == "": return
      if line == S.CRLF: break
      k, v = line.split(":", 1); headers[k.lower()] = v.strip()
    yield dict(
      start_line = start_line.rstrip(S.CRLF), headers = headers,
      body = si
    )
                                                                # }}}1

# TODO
def split_body(msg, bufsize):
  """..."""
  cl = int(msg["headers"].get("content-length", 0))
  return msg["body"].split(cl, bufsize)

# TODO
def requests(si, bufsize = S.DEFAULT_BUFSIZE):                  # {{{1
  """..."""
  for msg in generic_messages(si):
    method, uri, version = msg["start_line"].split(" ")
    co = msg["headers"].get("connection", "keep-alive").lower()
    body, si = split_body(msg, bufsize)
    yield dict(
      method = method, uri = uri, version = version,
      headers = msg["headers"], body = body
    )
    if co == "close":
      si.close()
      return
                                                                # }}}1

# TODO
def responses(si, bufsize = S.DEFAULT_BUFSIZE):                 # {{{1
  """..."""
  for msg in generic_messages(si):
    version, status, reason = msg["start_line"].split(" ", 2)
    body, si = split_body(msg, bufsize)
    yield dict(
      version = version, status = int(status), reason = reason,
      headers = msg["headers"], body = body
    )
                                                                # }}}1

# TODO
def evaluate_bodies(xs):
  """..."""
  for msg in xs:
    msg["body"] = msg["body"].read()
    yield msg

# ...

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
