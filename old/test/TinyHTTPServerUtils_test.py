# --                                                            ; {{{1
#
# File        : TinyHTTPServerUtils_test.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-02-26
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

import TinyHTTPServerUtils as U
import unittest

class Test_TinyHTTPServerUtils(unittest.TestCase):

  def test_crlf(self):
    x = ["foo", "bar", ""]
    y = "foo\r\nbar\r\n\r\n"
    self.assertEqual(U.crlf(x), y)

  def test_deindent(self):
    x = """
    foo
      bar
    baz
    """
    y = ["foo","  bar","baz"]
    self.assertEqual(U.deindent(x, 4), y)

  def test_lower_keys(self):
    x = { "User-Agent": "foo/1.2", "Foo": "Bar" }
    y = { "user-agent": "foo/1.2", "foo": "Bar" }
    self.assertEqual(U.lower_keys(x), y)

  def test_merge_dict(self):
    a   = dict(x = 42, y = 37)
    a_  = dict(x = 42, y = 37)
    b   = dict(z = 77, x = 99)
    b_  = dict(z = 77, x = 99)
    c   = dict(y = -1)
    c_  = dict(y = -1)
    d   = dict(x = 99, y = -1, z = 77)
    self.assertEqual(U.merge_dict(a, b, c), d)
    self.assertEqual(a, a_)
    self.assertEqual(b, b_)
    self.assertEqual(c, c_)

  def test_parse_headers_and_body(self):
    x = "Foo: 42\r\nBar-Baz: 37\r\n\r\n<body>"
    h = { "Foo": "42", "Bar-Baz": "37" }
    b = "<body>"
    y = dict(headers = h, body = b)
    self.assertEqual(U.parse_headers_and_body(x), y)

  # TODO
  def test_parse_request(self):
    pass

  def test_parse_response(self):
    x = "HTTP/1.1 200 OK\r\nServer: foo\r\n\r\n<body>"
    h = { "Server": "foo" }
    b = "<body>"
    y = dict(
      headers = h, body = b, version = "HTTP/1.1",
      status = 200, reason = "OK"
    )
    self.assertEqual(U.parse_response(x), y)

  # ...


if __name__ == "__main__":
  unittest.main()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
