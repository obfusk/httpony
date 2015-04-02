# --                                                            ; {{{1
#
# File        : httpony/handler.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-04-01
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

"""HTTP request handler dsl"""

from . import http as H
from . import stream as S
from . import util as U
import email.utils as EU
import hashlib
import os
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
    self.params   = request.params()
    self.headers  = U.idict()
    handler       = self._match(request)
    if handler is None: return None
    self.response = H.response(handler(self, *self.route_args))
    if self.response:
      for (k,v) in self.headers.iteritems():
        self.response.headers.setdefault(k, v)
    return self.response
                                                                # }}}2

  # TODO
  def _match(self, request):                                    # {{{2
    for h in self._handlers:
      methods, uri_pattern, handler = h
      if request.method in methods:
        m = uri_pattern.search(request.uri.path)
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
        p = re.compile(
          "\A" + "/".join(map(_pattern_to_regex,
                              uri_pattern.split("/"))) + "\Z"
        )
      if not hasattr(cls, "_handlers"): cls._handlers = []
      cls._handlers += [(methods, p, meth)]
      return meth
    # fed
    return decorate
                                                                # }}}2

  # TODO
  def redirect(self, uri, status = None):
    """redirect"""
    if status is None:
      status = 302 if self.request.method == "GET" else 303
    return H.response((status, dict(Location = uri), ""))

  # TODO
  def serve_file(self, path):                                   # {{{2
    """serve file"""
    s = os.stat(path); t = int(s.st_mtime)
    i = U.BY(str(t)) + b"|" + U.BY(str(s.st_size))
    e = hashlib.sha1(i).hexdigest()
    h = { "Last-Modified": EU.formatdate(t), "ETag": e }
    if "If-Modified-Since" in self.request.headers:
      ims = self.request.headers["If-Modified-Since"]
      t2  = int(EU.mktime_tz(EU.parsedate_tz(ims)))
      if t <= t2: return 304
    if "ETag" in self.request.headers:
      e2  = self.request.headers["ETag"]
      if e2 == "*" or e in re.split("\s+,\s+", e2): return 304
    return (200, h, S.ifile_stream(path))
                                                                # }}}2

  # ...
                                                                # }}}1

def _pattern_to_regex(x):
  if re.search("\A:[A-Za-z_][A-Za-z0-9_]+\Z", x):
    return "(?P<" + x[1:] + ">[^/]+)"
  elif x == "*":
    return "(.*)"
  else:
    return re.escape(x)

class _MethodWrapper(U.Immutable):
  __slots__ = "method call args".split()

# GET also handles HEAD; ANY handles any method
def _make_handler_classmethod(http_method):                     # {{{1
  if http_method == "ANY":
    methods = H.HTTP_METHODS
  elif http_method == "GET":
    methods = "GET HEAD".split()
  else:
    methods = [http_method]
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
  for k in list(d.keys()):
    if isinstance(d[k], _MethodWrapper):
      ws[k] = d[k]; del d[k]
  c = type(cls.__name__, (HandlerBase,), d)
  for (k, w) in U.iteritems(ws):
    setattr(c, k, getattr(c, w.call)(*w.args)(w.method))
  return c
                                                                # }}}1

# TODO: before, after, ...
for _m in ["ANY"] + H.HTTP_METHODS:
  setattr(HandlerBase, _m.lower(), _make_handler_classmethod(_m))
  locals()[_m.lower()] = _make_method_wrapper(_m)
del _m

# TODO
def context(*prefixes_and_handlers):                            # {{{1
  """new handler that dispatches based on prefix match"""
  dispatch = []
  for (p, h) in prefixes_and_handlers:
    if not isinstance(p, RE_TYPE):
      p = re.compile(
        "\A" + "/".join(map(_pattern_to_regex, p.split("/")))
      )
    dispatch += [(p, h)]
  def make_handler():
    def handler(request):
      for (p, h) in dispatch:
        m = p.search(request.uri.path)
        if m is not None:
          pre, path = m.string[:m.end()], m.string[m.end():]
          request.env["context"       ] += [pre]
          request.env["context_args"  ] += m.groups()
          request.env["context_params"].update(m.groupdict())
          return h()(request.with_uri(request.uri.with_path(path)))
    return handler
  return make_handler
                                                                # }}}1

# NB: remote_addr, scheme, server_addr, server_info should be set by
# the server
def handle(handler, request, env = None):
  """handle request"""
  if env: request.update_env(env)
  request.env.setdefault("context"        , [])
  request.env.setdefault("context_args"   , [])
  request.env.setdefault("context_params" , {})
  request.env.setdefault("original_uri"   , request.uri)
  return handler()(request) or H.response(404)

@handler
class Static:                                                   # {{{1

  """serve static assets"""

  path      = "."
  listdirs  = False

  index_pre = "\n".join(x.lstrip() for x in """
    <!DOCTYPE html>
    <html>
    <head>
    <title>Directory listing for /{0}</title>
    <meta http-equiv="content-type"
          content="text/html; charset=utf-8" />
    </head>
    <body>
    <h2>Directory listing for /{0}</h2>
    <hr />
    <ul>
  """.split("\n")[1:])

  index_entry = """<li><a href="{0}">{0}</a>\n"""

  index_post = "\n".join(x.lstrip() for x in """
    </ul>
    <hr />
    </body>
    </html>
  """.split("\n")[1:])

  # TODO
  @get("/*")
  def get_path(self, path):
    base    = os.path.join(os.path.abspath(self.path), "")
    fs_path = os.path.abspath(os.path.join(base, "./" + path))
    if not (fs_path + "/").startswith(base):
      return 403
    elif os.path.isfile(fs_path):
      return self.serve_file(fs_path)
    elif os.path.isdir(fs_path):
      index = os.path.join(fs_path, "index.html")
      if path and not path.endswith("/"):
        return self.redirect("/" + path + "/", 301)
      elif os.path.isfile(index):
        return self.serve_file(index)
      elif self.listdirs:
        return self.listdir(path, fs_path)
    return 404

  def listdir(self, path, fs_path):
    yield self.index_pre.format(U.escape_html(path))
    for x in sorted(x for x in os.listdir(fs_path)
                        if not x.startswith(".")):
      if os.path.isdir(os.path.join(fs_path, x)): x = x + "/"
      yield self.index_entry.format(U.escape_html(x))
    yield self.index_post
                                                                # }}}1

def static(path = ".", listdirs = False, name = "Static"):
  """create static asset handler"""
  return type(name, (Static,), dict(path = path, listdirs = listdirs))

# ...

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
