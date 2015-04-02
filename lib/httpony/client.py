# --                                                            ; {{{1
#
# File        : httpony/client.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-04-01
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

"""HTTP client"""

from . import handler as H
from . import http as HTTP
from . import stream as S
import httpony  # for DEFAULT_USER_AGENT
import socket
import ssl

try:
  import Queue as Q # python2
except ImportError:
  import queue as Q # python3

_CLIENTS = {}

# TODO
class Client(object):                                           # {{{1

  """HTTP client"""

  persistent = False

  def __init__(self, base_uri = "", handler = None,
               persistent = None,
               user_agent = httpony.DEFAULT_USER_AGENT):
    for m in ["request"] + [m.lower() for m in HTTP.HTTP_METHODS]:
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

  # TODO
  def default_env(self):
    """default env"""
    return dict(
      remote_addr = None,     # TODO
      scheme      = "http",   # TODO
      server_addr = None,     # TODO
      server_info = httpony.DEFAULT_USER_AGENT
    )

  def _merge_w_default_headers(self, headers = None):
    h = self.default_headers(); h.update(headers); return h

  def _socket(self, uri):
    sock = socket.socket()
    if uri.scheme == HTTP.HTTPS_SCHEME:
      ctx   = ssl.create_default_context()
      sock  = ctx.wrap_socket(sock, server_hostname = uri.host)
    sock.connect((uri.host, uri.port))
    return sock

  # TODO
  def _socket_request(self, reqs):
    prev = None; sock = None; resps = None
    try:
      while not reqs.empty():
        req = reqs.get()
        if not prev or prev.host_and_port != req.uri.host_and_port:
          if sock: sock.close()
          sock  = self._socket(req.uri)
          resps = HTTP.responses(S.ISocketStream(sock))
          so    = S.OSocketStream(sock)
        for chunk in req.unparse_chunked(): so.write(chunk)
        so.flush(); yield next(resps, None); prev = req.uri
    finally:
      if sock: sock.close()

  # TODO
  # "overloaded"
  def _i_request(self, method, uri, headers = None, body = None,
                 body_only = False):                            # {{{2
    headers = self._merge_w_default_headers(headers or {})
    if self.base_uri and (uri == "" or uri.startswith("/")):
      uri = self.base_uri + uri
    req = HTTP.Request(method = method, uri = uri,
                    headers = headers, body = body or "")
    if not req.uri.host: raise ValueError("no host specified")
    req.headers.setdefault("Host", req.uri.host_and_port)
    if self.handler:
      resp = H.handle(self.handler, req, self.default_env())
    elif self.persistent: # FIXME
      if not hasattr(self, "_reqs"):
        self._queue = Q.Queue()
        self._reqs  = self._socket_request(self._queue)
      self._queue.put(req); resp = next(self._reqs, None)
    else:
      req.headers["Connection"] = "close" # TODO
      q = Q.Queue(); q.put(req)
      resp = list(self._socket_request(q))[0]
    return resp.force_body if resp is not None and body_only else resp
                                                                # }}}2

  # TODO
  @classmethod
  def request(cls, method, uri, headers = None, body = None,
              body_only = False):
    """request w/ the specified method"""
    if cls not in _CLIENTS: _CLIENTS[cls] = Client()
    return _CLIENTS[cls].request(method, uri, headers, body,
                                 body_only)
                                                                # }}}1

def _make_request_methods(http_method):
  def f(self, uri, **kw): return self.request(http_method, uri, **kw)
  f.__name__  = http_method.lower()
  f.__doc__   = """{} request""".format(http_method)
  return f, classmethod(f)

for _m in HTTP.HTTP_METHODS:
  _f, _g = _make_request_methods(_m)
  setattr(Client, "_i_" + _m.lower(), _f)
  setattr(Client,         _m.lower(), _g)
del _m, _f, _g

# ...

# TODO
if __name__ == "__main__":
  pass

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
