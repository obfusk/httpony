# --                                                            ; {{{1
#
# File        : httpony/handler.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-06
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

"""HTTP request handler dsl"""

from . import http as H
from . import util as U
import re

RE_TYPE = type(re.compile(""))

# TODO
class HandlerBase(object):                                      # {{{1

  # TODO
  def __init__(self):
    pass

  # TODO
  def __call__(self, request):                                  # {{{2
    """handle request"""
    self.request  = request
    self.params   = {}
    handler       = self._match(request)
    if handler is None: return None
    self.response = H.response(handler(self, *self.route_args))
    return self.response
                                                                # }}}2

  # TODO
  def _match(self, request):                                    # {{{2
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
                                                                # }}}2

  # TODO
  @classmethod
  def request(cls, methods, uri_pattern):                       # {{{2
    """create request handler for the specified methods and pattern"""
    def decorate(meth):
      if cls is HandlerBase:
        raise TypeError("must not be called on HandlerBase itself")
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

  # ...
                                                                # }}}1

class _MethodWrapper(U.Immutable):
  __slots__ = "method call args".split()

def _make_handler_classmethod(http_method):                     # {{{1
  methods = [http_method] if http_method != "ANY" else H.HTTP_METHODS
  def f(cls, uri_pattern): return cls.request(methods, uri_pattern)
  f.__name__  = http_method.lower()
  f.__doc__   = """create {} request handler (decorator)""" \
                .format(http_method)
  return classmethod(f)
                                                                # }}}1

def _make_method_wrapper(http_method):                          # {{{1
  def f(uri_pattern):
    def decorate(meth):
      return _MethodWrapper(method = meth, call = http_method.lower(),
                            args = (uri_pattern,))
    return decorate
  f.__name__  = http_method.lower()
  f.__doc__   = """create {} request handler (decorator)""" \
                .format(http_method)
  return f
                                                                # }}}1

def Handler(name = "Handler"):
  """create Handler"""
  return type(name, (HandlerBase,), {})

def handler(cls):                                               # {{{1
  """create Handler from class (decorator)"""
  d = cls.__dict__.copy(); ws = {}
  for k in d.keys():
    if isinstance(d[k], _MethodWrapper):
      ws[k] = d[k]; del d[k]
  c = type(cls.__name__, (HandlerBase,), d)
  for (k, w) in ws.iteritems():
    setattr(c, k, getattr(c, w.call)(*w.args)(w.method))
  return c
                                                                # }}}1

# TODO: before, after, post, ...
for _x in "ANY GET".split():
  setattr(HandlerBase, _x.lower(), _make_handler_classmethod(_x))
  locals()[_x.lower()] = _make_method_wrapper(_x)
del _x

# ...

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
