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
import socket

_CLIENTS = {}

# TODO
class Client(object):                                           # {{{1

  """HTTP client"""

  persistent = False

  def __init__(self, base_uri = "", handler = None,
               persistent = None):
    for m in ["request"] + [m.lower() for m in H.HTTP_METHODS]:
      setattr(self, m, getattr(self, "_i_" + m)) # "overload"
    self.base_uri = base_uri; self.handler = handler
    if persistent is not None: self.persistent = persistent

  # TODO
  # "overloaded"
  def _i_request(self, method, uri, headers = None, body = None,
                 body_only = False):
    if headers is None: headers = {}
    if body is None: body = ""
    if self.base_uri and (uri == "" or uri.startswith("/")):
      uri = self.base_uri + uri
    req = H.Request(method = method, uri = uri,
                    headers = headers, body = body)
    if not req.uri.host: raise ValueError("no host specified")
    # TODO
    # not self.base_uri or req.uri.host_and_port ==
    #                      URI(self.base_uri).host_and_port
    import code; code.interact(local=locals()) # DEBUG
    if self.handler:
      resp = self.handler(req)
      return resp.force_body if body_only else resp
    elif self.persistent:
      pass # TODO
    else:
      pass # TODO

  # TODO
  @classmethod
  def request(cls, method, uri, headers = None, body = None,
              body_only = False):
    """request w/ the specified method"""
    if cls not in _CLIENTS: _CLIENTS[cls] = Client()
    _CLIENTS[cls].request(method, uri, headers, body, body_only)
                                                                # }}}1

def _make_request_methods(http_method):
  def f(self, uri, headers = None, body = None, body_only = False):
    return self.request(http_method, uri, headers, body, body_only)
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
