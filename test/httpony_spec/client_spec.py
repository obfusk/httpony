# --                                                            ; {{{1
#
# File        : client_spec.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-09
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

import httpony.client as C
import httpony.handler as H
import httpony.util as U
import unittest

X = H.Handler("X")

@X.any("/headers")
def the_rest(self):
  return (404, {}, repr(sorted(self.request.headers.items())))

@X.any("/*")
def the_rest(self, splat):
  return (404, {}, repr([self.request.method, self.request.uri.uri]))

# TODO
class Test_Client(unittest.TestCase):                           # {{{1

  def test_get_with_handler(self):
    c = C.Client(handler = X)
    x = c.get("example.com/foo")
    self.assertEqual(U.STR(x.force_body),
                     repr(["GET", "http://example.com/foo"]))

  def test_get_with_handler_headers(self):
    c = C.Client(handler = X)
    x = c.get("example.com/headers")
    self.assertEqual(U.STR(x.force_body),
                     repr([("Accept", "*/*"), ("Host", "example.com"),
                           ("User-Agent", C.DEFAULT_USER_AGENT)]))

  def test_post_with_handler(self):
    c = C.Client(handler = X)
    x = c.post("example.com/foo")
    self.assertEqual(U.STR(x.force_body),
                     repr(["POST", "http://example.com/foo"]))

  def test_get_with_handler_and_base_uri(self):
    c = C.Client("example.com", handler = X)
    x = c.get("/foo")
    y = c.get("/bar")
    z = c.get("example.org/baz")
    self.assertEqual(U.STR(x.force_body),
                     repr(["GET", "http://example.com/foo"]))
    self.assertEqual(U.STR(y.force_body),
                     repr(["GET", "http://example.com/bar"]))
    self.assertEqual(U.STR(z.force_body),
                     repr(["GET", "http://example.org/baz"]))

  # ...
                                                                # }}}1

# ...

if __name__ == "__main__":
  unittest.main()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
