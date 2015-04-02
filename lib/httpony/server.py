# --                                                            ; {{{1
#
# File        : httpony/server.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-04-02
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

"""HTTP server"""

from __future__ import print_function # DEBUG

from . import handler as H
from . import http as HTTP
from . import stream as S
from . import util as U
import collections
import httpony  # for DEFAULT_SERVER
import socket
import ssl
import sys

try:
  import SocketServer as SS # python2
except ImportError:
  import socketserver as SS # python3

DEFAULT_TIMEOUT = 10  # TODO

class _ThreadedTCPServer(SS.ThreadingMixIn, SS.TCPServer):
  scheme = HTTP.HTTP_SCHEME

class _ThreadedSSLTCPServer(_ThreadedTCPServer):                # {{{1

  scheme = HTTP.HTTPS_SCHEME

  def __init__(self, server_address, RequestHandlerClass,
               certfile, keyfile = None, password = None):
    self.ssl_config = dict(
      certfile = certfile, keyfile = keyfile, password = password
    )
    _ThreadedTCPServer.__init__(self, server_address,
                                RequestHandlerClass)

  def server_bind(self):
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(**self.ssl_config)
    self.socket = ctx.wrap_socket(self.socket, server_side = True)
    return _ThreadedTCPServer.server_bind(self)
                                                                # }}}1

# TODO
class Server(object):                                           # {{{1

  """HTTP server"""

  def __init__(self, handler, server_info = httpony.DEFAULT_SERVER):
    self.handler = handler; self.server_info = server_info

  # TODO
  def default_headers(self, rh):
    """default headers"""
    return {
      "Server"      : self.server_info,
      "Keep-Alive"  : "timeout={}".format(rh.timeout)
    }

  # TODO
  def default_env(self, rh):
    """default env"""
    return dict(
      remote_addr = rh.client_address,
      scheme      = rh.server.scheme,
      server_addr = rh.server.server_address,
      server_info = self.server_info
    )

  # TODO
  def _requesthandler(self):                                    # {{{2
    class RequestHandler(SS.StreamRequestHandler):

      timeout = DEFAULT_TIMEOUT

      # TODO; DEBUG
      def handle(self):
        s = self.httpony_server
        try:
          print("connect {}".format(self.client_address))
          reqs  = HTTP.requests(S.IRequestHandlerStream(self))
          so    = S.ORequestHandlerStream(self)
          for req in reqs:
            print("request {} {}".format(req.method, req.uri.uri))
            with_body = req.method != "HEAD"  # TODO
            resp = H.handle(s.handler, req, s.default_env(self))
            for (k, v) in U.iteritems(s.default_headers(self)):
              resp.headers.setdefault(k, v)
            if req.headers.get("Connection", "").lower() == "close":
              resp.headers["Connection"] = "close"
            for chunk in resp.unparse_chunked(with_body):
              so.write(chunk)
            so.flush()
            print("response {}".format(resp.status))
          print("disconnect {}".format(self.client_address))
        except socket.timeout:
          print("timeout!") # TODO
        except ssl.SSLError as e:
          if e.message.find("read operation timed out") != -1:
            print("ssl timeout!") # TODO
          else:
            raise

    RequestHandler.httpony_server = self
    return RequestHandler
                                                                # }}}2

  def run(self, host = "localhost", port = None, ssl = None,
          timeout = None):                                      # {{{2
    """run the server"""
    if port is None:
      port = HTTP.HTTP_DEFAULT_PORT if not ssl else \
             HTTP.HTTPS_DEFAULT_PORT
    self.requesthandler = self._requesthandler()
    if timeout is not None:
      self.requesthandler.timeout = timeout
    args = [(host, port), self.requesthandler]
    if ssl:
      if isinstance(ssl, collections.Mapping):
        server = _ThreadedSSLTCPServer(*args, **dict(ssl))
      else:
        server = _ThreadedSSLTCPServer(*(args + list(ssl)))
    else:
      server = _ThreadedTCPServer(*args)
    try:
      print("listening on {}:{}".format(host, port))
      server.serve_forever()
    except KeyboardInterrupt:
      server.shutdown()
                                                                # }}}2
                                                                # }}}1

# ...

# TODO
if __name__ == "__main__":
  opts = dict( x.split("=", 1) for x in sys.argv[1:] )
  s = Server(H.static(path = opts.get("path", "."), listdirs = True))
  s.run(port    = int(opts.get("port", 8000)),
        timeout = int(opts.get("timeout", DEFAULT_TIMEOUT)))

# X = H.Handler()
# @X.get("/*")
# def foo(self, splat):
#   print(repr(self.request)+"\n")
#   return (x for x in ["Hi ...\n", "... there!\n"])
# Y = H.context(
#   ("/foo", X), ("/:bar", H.context(("/foo/:qux", X))),
#   ("/", X)
# )
# Server(Y).run(port = 8000, ssl = ("test-data/ssl/localhost.crt",
#                                   "test-data/ssl/localhost.key"))

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
