# --                                                            ; {{{1
#
# File        : httpony/server.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-09
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

"""HTTP server"""

from . import http as H
from . import stream as S
import collections
import httpony  # for __version__
import socket
import SocketServer
import ssl

DEFAULT_SERVER = "httpony.server/{}".format(httpony.__version__)

class _ThreadedTCPServer(SocketServer.ThreadingMixIn,
                         SocketServer.TCPServer):
  pass

class _ThreadedSSLTCPServer(_ThreadedTCPServer):                # {{{1

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

  def __init__(self, handler, server_info = DEFAULT_SERVER):
    self.handler = handler; self.server_info = server_info

  # TODO
  def default_headers(self):
    """default headers"""
    return {
      "Server" : self.server_info
    }

  # TODO
  def _requesthandler(self):                                    # {{{2
    class RequestHandler(SocketServer.StreamRequestHandler):

      timeout = 10 # TODO

      # TODO
      def handle(self):
        s = self.httpony_server
        try:
          print "connect {}".format(self.client_address) # DEBUG
          reqs  = H.requests(S.IRequestHandlerStream(self))
          so    = S.ORequestHandlerStream(self)
          for req in reqs:
            # ... self.client_address ... chunked ...
            resp = s.handler()(req)
            for (k, v) in s.default_headers().iteritems():
              resp.headers.setdefault(k, v)
            resp.headers["Content-Length"] = len(resp.force_body)
            so.write(resp.unparse()); so.flush()
          print "disconnect {}".format(self.client_address) # DEBUG
        except socket.timeout:
          print "timeout!" # TODO
        except ssl.SSLError as e:
          if e.message.find("read operation timed out") != -1:
            print "timeout!" # TODO
          else:
            raise

    RequestHandler.httpony_server = self
    return RequestHandler
                                                                # }}}2

  def run(self, host = "localhost", port = None, ssl = None):   # {{{2
    """run the server"""
    if port is None:
      port = H.HTTP_DEFAULT_PORT if not ssl else HTTPS_DEFAULT_PORT
    self.requesthandler = self._requesthandler()
    args = [(host, port), self.requesthandler]
    if ssl:
      if isinstance(ssl, collections.Mapping):
        server = _ThreadedSSLTCPServer(*args, **dict(ssl))
      else:
        server = _ThreadedSSLTCPServer(*(args + list(ssl)))
    else:
      server = _ThreadedTCPServer(*args)
    try:
      server.serve_forever()
    except KeyboardInterrupt:
      server.shutdown()
                                                                # }}}2
                                                                # }}}1

# ...

# TODO
if __name__ == "__main__":
  pass

# from . import handler
# X = handler.Handler()
# @X.any("/*")
# def foo(self, splat): print repr(self.request)+"\n"; return "Hi!\n"
# Server(X).run(port = 8000, ssl = ("/tmp/ssl/localhost.crt",
#                                   "/tmp/ssl/localhost.key"))

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
