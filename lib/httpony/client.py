# --                                                            ; {{{1
#
# File        : httpony/client.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-06
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

"""HTTP client"""

from . import http as H
from . import stream as S
import httpony  # for __version__
import socket
import ssl

DEFAULT_USER_AGENT = "httpony.client/{}".format(httpony.__version__)

_CLIENTS = {}

# TODO
class Client(object):                                           # {{{1

  """HTTP client"""

  persistent = False

  def __init__(self, base_uri = "", handler = None,
               persistent = None, user_agent = DEFAULT_USER_AGENT):
    for m in ["request"] + [m.lower() for m in H.HTTP_METHODS]:
      setattr(self, m, getattr(self, "_i_" + m)) # "overload"
    self.base_uri   = base_uri; self.handler = handler
    self.user_agent = user_agent
    if persistent is not None: self.persistent = persistent

  def default_headers(self):
    """default headers"""
    return {
      "Accept"      : "*/*",
      "User-Agent"  : self.user_agent
    }

  def _merge_w_default_headers(self, headers = None):
    h = self.default_headers(); h.update(headers); return h

  def _socket(self, uri):
    sock = socket.socket()
    if uri.scheme == H.HTTPS_SCHEME:
      ctx   = ssl.create_default_context()
      sock  = ctx.wrap_socket(sock, server_hostname = uri.host)
    sock.connect((uri.host, uri.port))
    return sock

  # TODO
  def _socket_request(self, req):
    sock  = self._socket(req.uri)
    reqs  = H.responses(S.ISocketStream(sock))
    so    = S.OSocketStream(sock)
    resp  = None
    try:
      for chunk in req.unparse(): so.write(chunk)
      so.flush(); resp = next(reqs, None);
    finally:
      sock.close()
    return resp

  # TODO
  # "overloaded"
  def _i_request(self, method, uri, headers = None, body = None,
                 body_only = False):                            # {{{2
    headers = self._merge_w_default_headers(headers or {})
    if self.base_uri and (uri == "" or uri.startswith("/")):
      uri = self.base_uri + uri
    req = H.Request(method = method, uri = uri,
                    headers = headers, body = body or "")
    if not req.uri.host: raise ValueError("no host specified")
    req.headers.setdefault("Host", req.uri.host)
    if self.handler:
      resp = self.handler(req)
    elif self.persistent:
      # TODO: we need to check whether host_and_port is the same
      raise RuntimeError("persistent connections not yet implemented")
    else:
      req.headers["Connection"] = "close" # TODO
      resp = self._socket_request(req)
    return resp.force_body if body_only else resp
                                                                # }}}2

  # TODO
  @classmethod
  def request(cls, method, uri, headers = None, body = None,
              body_only = False):
    """request w/ the specified method"""
    if cls not in _CLIENTS: _CLIENTS[cls] = Client()
    _CLIENTS[cls].request(method, uri, headers, body, body_only)
                                                                # }}}1

def _make_request_methods(http_method):
  def f(self, uri, **kw): return self.request(http_method, uri, **kw)
  f.__name__  = http_method.lower()
  f.__doc__   = """{} request""".format(http_method)
  return f, classmethod(f)

for _m in H.HTTP_METHODS:
  _f, _g = _make_request_methods(_m)
  setattr(Client, "_i_" + _m.lower(), _f)
  setattr(Client,         _m.lower(), _g)
del _m, _f, _g

# ...

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
