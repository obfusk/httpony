# --                                                            ; {{{1
#
# File        : http_spec.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-04
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

import httpony.http as H
import httpony.stream as S
import httpony.util as U
import unittest

class Test_Request(unittest.TestCase):                          # {{{1

  def test_init_empty(self):
    x = H.Request()
    self.assertEqual(
      dict(x.iteritems()),  # also tests iteritems
      dict(
        method = "GET", uri = "/", version = "HTTP/1.1",
        headers = U.idict(), body = ("",), env = {}
      )
    )

  def test_init_kwds(self):
    x = H.Request(method = "POST", uri = "/foo",
                  headers = dict(Foo = "bar"), body = "<body>")
    self.assertEqual(
      dict(x.iteritems()),
      dict(
        method = "POST", uri = "/foo", version = "HTTP/1.1",
        headers = U.idict(Foo = "bar"), body = ("<body>",), env = {}
      )
    )

  def test_init_dict(self):
    x = H.Request(dict(method = "POST", uri = "/foo",
                       headers = dict(Foo = "bar"), body = "<body>"))
    self.assertEqual(
      dict(x.iteritems()),
      dict(
        method = "POST", uri = "/foo", version = "HTTP/1.1",
        headers = U.idict(Foo = "bar"), body = ("<body>",), env = {}
      )
    )

  def test_init_kwds_unknown(self):
    with self.assertRaisesRegexp(TypeError, "unknown keys"):
      H.Request(foo = 42)

  def test_init_no_kwds_and_data(self):
    with self.assertRaisesRegexp(TypeError, "arguments must either " +
                                            "be data or keywords"):
      H.Request("<body>", method = "POST")

  def test_init_data_no_mapping(self):
    with self.assertRaisesRegexp(TypeError, "must be a mapping"):
      H.Request("hi!")

  def test_init_headers(self):
    x = H.Request(headers = dict(x = 37, y = 42))
    self.assertIsInstance(x.headers, U.idict)
    self.assertEqual(x.headers, U.idict(x = 37, Y = 42))

  def test_init_body_str(self):
    x = H.Request(body = "<body>")
    self.assertEqual(x.body, ("<body>",))

  def test_init_body_IStream(self):
    x = H.Request(body = S.IStringStream("<body>"))
    self.assertIsInstance(x.body, type(x for x in []))
    self.assertEqual("".join(x.body), "<body>")

  def test_force_body(self):
    x = H.Request(body = (x for x in "foo bar baz".split()))
    self.assertIsInstance(x.body, type(x for x in []))
    self.assertEqual(x.force_body(), "foobarbaz")
    self.assertIsInstance(x.body, tuple)
    self.assertEqual(x.body, ("foobarbaz",))

  def test_no_setattr(self):
    x = H.Request()
    with self.assertRaisesRegexp(AttributeError,
                                 "'Request' object " +
                                 "attribute 'body' is read-only"):
      x.body = 99

  def test_no_setattr_new(self):
    x = H.Request()
    with self.assertRaisesRegexp(AttributeError,
                                 "'Request' object " +
                                 "has no attribute 'foo'"):
      x.foo = 99

  def test_eq(self):
    x = H.Request(body = "foo")
    y = H.Request(body = "bar")
    self.assertEqual(x, x)
    self.assertNotEqual(x, y)

  def test_cmp(self):
    x = H.Request(body = "foo")
    y = H.Request(body = "bar")
    self.assertGreater(x, y)
    self.assertGreaterEqual(x, y)
    self.assertGreaterEqual(x, x)
    self.assertLess(y, x)
    self.assertLessEqual(y, x)

  def test_repr(self):
    x = H.Request(body = "<body>")
    y = [("method", "GET"), ("uri", "/"), ("version", "HTTP/1.1"),
         ("headers", U.idict()), ("body", ("<body>",)), ("env", {})]
    self.assertEqual(
      repr(x),
      "Request({})".format(
        ", ".join("{} = {}".format(k, repr(v))
                  for (k,v) in y)
      )
    )

  def test_unparse(self):
    x = H.Request(method = "POST", uri = "/foo",
                  headers = dict(Foo = "bar", X = "42"),
                  body = "<body>")
    self.assertRegexpMatches(
      x.unparse(),
      "POST /foo HTTP/1.1\r\n((Foo|X): (bar|42)\r\n)+\r\n<body>"
    )
                                                                # }}}1

class Test_Response(unittest.TestCase):                         # {{{1

  # NB: the tests for Request cover most of the common functionality
  # provided by Message

  def test_init_kwds(self):
    x = H.Response(status = 404, headers = dict(Foo = "bar"))
    self.assertEqual(
      dict(x.iteritems()),
      dict(
        version = "HTTP/1.1", status = 404, reason = "Not Found",
        headers = U.idict(Foo = "bar"), body = ("",)
      )
    )

  def test_init_data_no_mapping_etc(self):
    with self.assertRaisesRegexp(TypeError, "must be a mapping, " +
                                "3-tuple, int, str, or iterable"):
      H.Response(3.14)

  def test_init_data_tuple(self):
    x = H.Response((404, dict(Foo = "bar"), "<body>"))
    self.assertEqual(
      dict(x.iteritems()),
      dict(
        version = "HTTP/1.1", status = 404, reason = "Not Found",
        headers = U.idict(Foo = "bar"), body = ("<body>",)
      )
    )

  def test_init_data_int(self):
    x = H.Response(500)
    self.assertEqual(
      dict(x.iteritems()),
      dict(
        version = "HTTP/1.1", status = 500,
        reason = "Internal Server Error",
        headers = U.idict(), body = ("",)
      )
    )

  def test_init_data_str(self):
    x = H.Response("<body>")
    self.assertEqual(
      dict(x.iteritems()),
      dict(
        version = "HTTP/1.1", status = 200, reason = "OK",
        headers = U.idict(), body = ("<body>",)
      )
    )

  def test_eq(self):
    x = H.Response(200)
    y = H.Response(404)
    self.assertEqual(x, x)
    self.assertNotEqual(x, y)

  def test_unparse(self):
    x = H.Response(status = 200,
                   headers = dict(Foo = "bar", X = "42"),
                   body = "<body>")
    self.assertRegexpMatches(
      x.unparse(),
      "HTTP/1.1 200 OK\r\n((Foo|X): (bar|42)\r\n)+\r\n<body>"
    )
                                                                # }}}1

class Test_http(unittest.TestCase):                             # {{{1

  def test_requests_w_forced_bodies(self):
    r1  = "GET /foo HTTP/1.1\r\nContent-length: 7\r\n\r\n<body1>"
    r2  = "GET /bar HTTP/1.1\r\nContent-length: 7\r\n\r\n<body2>"
    self.assertEqual(
      list(H.force_bodies(H.requests(S.IStringStream(r1 + r2)))),
      [
        H.Request(
          method = "GET", uri = "/foo",
          headers = { "content-length": "7" }, body = "<body1>"
        ),
        H.Request(
          method = "GET", uri = "/bar",
          headers = { "content-length": "7" }, body = "<body2>"
        )
      ]
    )

  def test_responses_w_forced_bodies(self):
    r1  = "HTTP/1.1 200 OK\r\nContent-length: 6\r\n\r\n<body>"
    r2  = "HTTP/1.1 404 Not Found\r\n\r\n"
    self.assertEqual(
      list(H.force_bodies(H.responses(S.IStringStream(r1 + r2)))),
      [
        H.Response(
          status = 200, reason = "OK",
          headers = { "content-length": "6" }, body = "<body>"
        ),
        H.Response(
          status = 404, reason = "Not Found", headers = {}, body = ""
        )
      ]
    )
                                                                # }}}1

# ...

if __name__ == "__main__":
  unittest.main()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
