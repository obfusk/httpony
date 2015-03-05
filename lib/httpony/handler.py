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
import re

RE_TYPE = type(re.compile(""))

# TODO
class _HandlerBase(object):                                     # {{{1

  """request handler base class"""

  def __init__(self):
    pass

  # TODO
  def __call__(self, request):
    """handle request"""
    self.request  = request
    self.params   = {}
    handler = self._match(request)
    if handler is None: return None                             # TODO
    self.response = handler(request)
    return self.response

  # TODO
  def _match(self, request):
    for h in self._handlers:
      methods, uri_pattern, handler = h
      if request.method in methods:
        m = uri_pattern.search(self, request.uri)
        if m is not None:
          self.route_args   = m.groups()
          self.route_params = m.groupdict()
          self.params.update(self.route_params)
          handler(self, request, *self.route_args,
                  **self.route_params)
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
      def handle(self, request, *a, **k):
        print "HANDLING", request                               # TODO
        return meth(self, request, *a, **k)
      # fed
      if not hasattr(cls, "_handlers"): cls._handlers = []
      cls._handlers += [(methods, p, handle)]
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

def Handler(name = ""):
  return type(name + "Handler", (_HandlerBase,), {})

# ...

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
