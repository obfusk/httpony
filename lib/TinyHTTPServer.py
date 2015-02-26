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

VERSION           = '0.0.1'

DEFAULT_PORT      = 80
DEFAULT_BUFSIZE   = 1024
DEFAULT_AGENT     = "tiny-http-server/{}".format(VERSION)

CRLF              = "\r\n"

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
  pass

def _crlf(xs):
  return ''.join(map(lambda x: x + CRLF, xs))

def _deindent(x, n):
  return map(lambda x: x[n:], x.split('\n')[1:-1])

class Server:
  class TCPHandler(SocketServer.StreamRequestHandler):
    def handle(self):
      data = self.rfile.readline().strip()
      self.wfile.write(data.upper())

class Client:

  REQUEST = _deindent("""
    {method} {url} HTTP/1.1
    User-Agent: {agent}
    Connection: close

  """, 4)

  def __init__(self, host = 'localhost', port = DEFAULT_PORT,
               bufsize = DEFAULT_BUFSIZE, user_agent = DEFAULT_AGENT):
    self.__dict__.update(host=host, port=port, bufsize=bufsize,
                         user_agent=user_agent)

  def _with_socket(self, f):
    try:
      sock = socket.socket(); sock.connect((self.host, self.port))
      x = f(sock)
    finally:
      sock.close()
    return x

  def _request(self, url, headers = {}):
    return _crlf(self.REQUEST).format(method = 'GET', url = url,
                 agent = self.user_agent)

  def get(self, url, params = {}, headers = {}):
    def f(sock):
      sock.sendall(self._request(url))
      data_i = ""
      while True:
        x = sock.recv(self.bufsize); data_i += x
        if not x: break
      return data_i
    return self._with_socket(f)

def test():
  x = Client(port = 4567)
  print x.get('/'),

if __name__ == '__main__':
  test()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
