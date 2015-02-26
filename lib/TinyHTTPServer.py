# --                                                            ; {{{1
#
# File        : TinyHTTPServer.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-02-26
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

import socket
import SocketServer
import sys

import TinyHTTPServerUtils as Utils

VERSION           = "0.0.1"

DEFAULT_PORT      = 80
DEFAULT_BUFSIZE   = 1024
DEFAULT_AGENT     = "tiny-http-server/{}".format(VERSION)

METHOD_GET        = "GET"


class ThreadedTCPServer(SocketServer.ThreadingMixIn,
                        SocketServer.TCPServer):
  pass


class Server:

  """HTTP Server"""

  class TCPHandler(SocketServer.StreamRequestHandler):

    # TODO
    def handle(self):
      data = self.rfile.readline().strip()
      self.wfile.write(data.upper())

  # ...


class Client:

  """HTTP Client"""

  # TODO: handle POST, ...; optimize?

  REQUEST = ["{method} {url} HTTP/1.1", "{headers}"]

  def __init__(self, host = "localhost", port = DEFAULT_PORT,
               bufsize = DEFAULT_BUFSIZE, user_agent = DEFAULT_AGENT):
    self.__dict__.update(
      host = host, port = port, bufsize = bufsize,
      user_agent = user_agent
    )

  def _with_socket(self, f):
    """run f(socket); returns return value of f"""
    try:
      sock = socket.socket(); sock.connect((self.host, self.port))
      x = f(sock)
    finally:
      sock.close()
    return x

  def default_headers(self):
    """default headers; e.g. user agent, host"""
    return {
      "User-Agent"  : self.user_agent,
      "Host"        : "{}:{}".format(self.host, self.port),
      "Accept"      : "*/*",
      "Connection"  : "close"                                   # TODO
    }

  def request(self, url, method = METHOD_GET, headers = {},
              default_headers = True):
    """create request from method, url, headers; adds default headers
    unless default_headers = False"""
    h1 = self.default_headers().copy() if default_headers else {}
    h1.update(headers)
    h2 = Utils.crlf(map(lambda (k,v): "{}: {}".format(k,v),
                   h1.items()))
    return Utils.crlf(self.REQUEST).format(
      method = method, url = url, headers = h2
    )

  # TODO: handle body, params
  def do_request(self, url, method = METHOD_GET, params = {},
                 headers = {}, default_headers = True, raw = False,
                 body = None):
    """make request; return dict (or raw request)"""
    def f(sock):
      req = self.request(url, method, headers, default_headers)
      sock.sendall(req); resp = ""
      while True:                                               # TODO
        x = sock.recv(self.bufsize); resp += x
        if not x: break
      return Utils.parse_response(resp) if not raw else resp
    return self._with_socket(f)

  def get(self, url, params = {}, headers = {},
          default_headers = True, raw = False):
    """GET request"""
    return self.do_request(
      url, METHOD_GET, params, headers, default_headers, raw
    )

  # ...


# TODO
def test():
  import pprint
  pp = pprint.PrettyPrinter(indent=2)
  x = Client(port = 4567)
  for line in x.request("/").splitlines():
    print "> " + line
  print
  resp = x.get("/", raw = True)
  for line in resp.splitlines():
    print "< " + line
  print
  pp.pprint(Utils.parse_response(resp))


if __name__ == "__main__":
  test()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
