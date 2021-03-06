# --                                                            ; {{{1
#
# File        : handler_spec.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-04-01
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

import httpony.handler as H
import httpony.http as HTTP
import unittest

X = H.Handler("X")

@X.get("/foo/:id")
def get_foo(self, id):
  return "got foo w/ id {}".format(id)

@X.get("/nothing/to/see")
def oops(self):
  return (404, {}, "oops")

@X.any("/*")
def the_rest(self, splat):
  return (404, {}, splat)

@H.handler
class Y:                                                        # {{{1

  @H.get("/bar/:id")
  def get_bar(self, id):
    return "got bar w/ id {}".format(id)

  @H.get("/nothing/to/see")
  def oops(self):
    return 404
                                                                # }}}1

class Test_Handler(unittest.TestCase):                          # {{{1

  def test_get_foo(self):
    req   = HTTP.Request(uri = "/foo/42")
    resp  = X()(req)
    self.assertEqual(resp, HTTP.Response(body = "got foo w/ id 42"))

  def test_oops(self):
    req   = HTTP.Request(uri = "/nothing/to/see")
    resp  = X()(req)
    self.assertEqual(resp, HTTP.Response(status = 404, body = "oops"))

  def test_the_rest(self):
    req   = HTTP.Request(uri = "/something/else")
    resp  = X()(req)
    self.assertEqual(resp, HTTP.Response(status = 404,
                                         body = "something/else"))

  def test_the_rest_post(self):
    req   = HTTP.Request(uri = "/some/where", method = "POST")
    resp  = X()(req)
    self.assertEqual(resp, HTTP.Response(status = 404,
                                         body = "some/where"))
                                                                # }}}1

class Test_handler(unittest.TestCase):                          # {{{1

  def test_get_foo(self):
    req   = HTTP.Request(uri = "/bar/37")
    resp  = Y()(req)
    self.assertEqual(resp, HTTP.Response(body = "got bar w/ id 37"))

  def test_oops(self):
    req   = HTTP.Request(uri = "/nothing/to/see")
    resp  = Y()(req)
    self.assertEqual(resp, HTTP.Response(status = 404))
                                                                # }}}1

# ...

if __name__ == "__main__":
  unittest.main()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
