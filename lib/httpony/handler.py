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
class HandlerBase(object):                                      # {{{1

  """request handler base class"""

  def __init__(self):
    pass

  # TODO
  def __call__(self, request):
    """handle request"""
    # ...
    handler = self._match(request)
    # ...
    return handler(request)

  # TODO
  def _match(self, request):
    for h in self._handlers:
      methods, uri_pattern, f = h
      if request.method in methods:
        m = uri_pattern.search(self, request.uri)
        if m is not None:
          a = m.groups(); d = m.groupdict()
          pass # TODO
    return None

  # TODO
  @classmethod
  def request(cls, methods, uri_pattern):
    """handle request of the specified methods and pattern"""
    def request_(meth):
      if cls is HandlerBase:
        raise TypeError("not a subclass of HandlerBase")        # TODO
      if not isinstance(uri_pattern, RE_TYPE):
        def f(x):
          if re.search("\A:\w+\Z", x):
            return "(?P<" + x[1:] + ">[^/]+)"
          elif x == "*":
            return ".*"
          else:
            return re.escape(x)
        p = re.compile(
          "\A" + "/".join(map(f, uri_pattern.split("/"))) + "\Z"
        )
      else:
        p = uri_pattern
      def handle(self, request):
        print "HANDLING", request                               # TODO
        return meth(self, request)
      if not hasattr(cls, "_handlers"): cls._handlers = []
      cls._handlers += [(methods, p, handle)]
      return meth
    return request_

  @classmethod
  def get(cls, uri_pattern):
    """handle GET request"""
    return cls.request(["GET"], uri_pattern)

  # TODO: before, after, any, post, ...

  # ...
                                                                # }}}1

def Handler(name = ""):
  return type("Handler", (HandlerBase,), {})

# ...

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
