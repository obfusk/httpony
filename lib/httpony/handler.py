# --                                                            ; {{{1
#
# File        : httpony/handler.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-05
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

from . import http as H
from . import util as U
import re

RE_TYPE = type(re.compile(""))

# TODO
class _HandlerBase(object):                                     # {{{1

  def __init__(self):
    pass

  # TODO
  def __call__(self, request):
    """handle request"""
    self.request  = request
    self.params   = {}
    handler       = self._match(request)
    if handler is None: return None
    self.response = H.Response(handler(self, *self.route_args))
    return self.response

  # TODO
  def _match(self, request):
    for h in self._handlers:
      methods, uri_pattern, handler = h
      if request.method in methods:
        m = uri_pattern.search(request.uri.relative_uri)
        if m is not None:
          self.route_args   = m.groups()
          self.route_params = m.groupdict()
          self.params.update(self.route_params)
          return handler
    return None

  # TODO
  @classmethod
  def request(cls, methods, uri_pattern):                       # {{{2
    """create request handler for the specified methods and pattern"""
    def decorate(meth):
      if cls is _HandlerBase:
        raise TypeError("not a subclass of _HandlerBase")
      if isinstance(uri_pattern, RE_TYPE):
        p = uri_pattern
      else:
        def f(x):
          if re.search("\A:[A-Za-z_][A-Za-z0-9_]+\Z", x):
            return "(?P<" + x[1:] + ">[^/]+)"
          elif x == "*":
            return "(.*)"
          else:
            return re.escape(x)
        # fed
        p = re.compile(
          "\A" + "/".join(map(f, uri_pattern.split("/"))) + "\Z"
        )
      if not hasattr(cls, "_handlers"): cls._handlers = []
      cls._handlers += [(methods, p, meth)]
      return meth
    # fed
    return decorate
                                                                # }}}2

  @classmethod
  def get(cls, uri_pattern):
    """handle GET request"""
    return cls.request(["GET"], uri_pattern)

  # TODO: before, after, any, post, ...

  # ...
                                                                # }}}1

class _MethodWrapper(U.Immutable):
  __slots__ = "method call args".split()

def Handler(name = "Handler"):
  """create Handler"""
  return type(name, (_HandlerBase,), {})

def handler(cls):                                               # {{{1
  """create Handler from class (with this decorator)"""
  d = cls.__dict__.copy(); ws = {}
  for k in d.keys():
    if isinstance(d[k], _MethodWrapper):
      ws[k] = d[k]; del d[k]
  c = type(cls.__name__, (_HandlerBase,), d)
  for (k, w) in ws.iteritems():
    setattr(c, k, getattr(c, w.call)(*w.args)(w.method))
  return c
                                                                # }}}1

def get(uri_pattern):
  """handle GET request"""
  def decorate(meth):
    return _MethodWrapper(method = meth, call = "get",
                          args = (uri_pattern,))
  return decorate

# TODO: before, after, any, post, ...

# ...

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
