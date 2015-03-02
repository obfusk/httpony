# --                                                            ; {{{1
#
# File        : httpony/server.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-01
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

from . import http as H
from . import stream as S
import socket
import SocketServer

# ...


# DEBUG
def test():

  import sys

  class ThreadedTCPServer(SocketServer.ThreadingMixIn,
                          SocketServer.TCPServer):
    pass

  class TCPHandler(SocketServer.StreamRequestHandler):

    timeout = 1

    def handle(self):
      try:
        print "handling ({}) ...".format(self.client_address)
        def f(si):
          for msg in si:
            print str(msg)
            yield "HTTP/1.1 200 OK\r\nContent-length: 4\r\n\r\nhi!\n"
        S.interact(
          H.requests(S.IRequestHandlerStream(self)),
          S.ORequestHandlerStream(self),
          f
        )
        print "done ({}).".format(self.client_address)
      except socket.timeout:
        print "timeout ({}).".format(self.client_address)

  print "starting..."
  server = ThreadedTCPServer(("localhost", 8000), TCPHandler)
  try:
    server.serve_forever()
  except KeyboardInterrupt:
    sys.exit(0)

# DEBUG
if __name__ == "__main__":
  test()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
