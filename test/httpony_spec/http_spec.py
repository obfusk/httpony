# --                                                            ; {{{1
#
# File        : http_spec.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-04-01
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

import httpony.http as H
import httpony.stream as S
import httpony.util as U
import unittest

class Test_URI(unittest.TestCase):                              # {{{1

  def setUp(self):
    self.a = "example.com:666/foo?x=42"
    self.b = "http://foo@example.com/foo?x=42&y=37&x=99#bar"
    self.c = "https://example.org/baz"
    self.x = H.URI(self.a)
    self.y = H.URI(self.b)
    self.z = H.URI(self.c)

  def test_attrs(self):
    self.assertEqual(self.x.scheme        , "http")
    self.assertEqual(self.x.username      , None)
    self.assertEqual(self.x.password      , None)
    self.assertEqual(self.x.host          , "example.com")
    self.assertEqual(self.x.port          , 666)
    self.assertEqual(self.x.path          , "/foo")
    self.assertEqual(self.x.query         , "x=42")
    self.assertEqual(self.x.query_params  , dict(x = "42"))
    self.assertEqual(self.x.fragment      , "")

    self.assertEqual(self.y.scheme        , "http")
    self.assertEqual(self.y.username      , "foo")
    self.assertEqual(self.y.password      , None)
    self.assertEqual(self.y.host          , "example.com")
    self.assertEqual(self.y.port          , 80)
    self.assertEqual(self.y.path          , "/foo")
    self.assertEqual(self.y.query         , "x=42&y=37&x=99")
    self.assertEqual(self.y.query_params  ,
                     dict(x = ["42", "99"], y = "37"))
    self.assertEqual(self.y.fragment      , "bar")

    self.assertEqual(self.z.scheme        , "https")
    self.assertEqual(self.z.username      , None)
    self.assertEqual(self.z.password      , None)
    self.assertEqual(self.z.host          , "example.org")
    self.assertEqual(self.z.port          , 443)
    self.assertEqual(self.z.path          , "/baz")
    self.assertEqual(self.z.query         , "")
    self.assertEqual(self.z.query_params  , dict())
    self.assertEqual(self.z.fragment      , "")

  def test_props(self):
    self.assertEqual(self.x.host_and_port, "example.com:666")
    self.assertEqual(self.x.uri, "http://" + self.a)
    self.assertEqual(self.x.schemeless_uri, self.a)
    self.assertEqual(self.x.relative_uri, self.a[self.a.index("/"):])
    self.assertEqual(self.x.uri_with_fragment, "http://" + self.a)

    self.assertEqual(self.y.host_and_port, "example.com")
    self.assertEqual(self.y.uri_with_fragment, self.b)

    self.assertEqual(self.z.host_and_port, "example.org")
    self.assertEqual(self.z.uri, self.c)
    self.assertEqual(self.z.schemeless_uri, self.c[8:])
    self.assertEqual(self.z.relative_uri, "/baz")

  def test_eq(self):
    self.assertEqual(self.x, self.x.uri)
    self.assertEqual(self.x, self.x.uri_with_fragment)
    self.assertEqual(self.y, self.y.uri_with_fragment)
                                                                # }}}1

class Test_Request(unittest.TestCase):                          # {{{1

  def test_init_empty(self):
    x = H.Request()
    self.assertEqual(
      dict(x.iteritems()),  # also tests iteritems
      dict(
        method = "GET", uri = "/", version = "HTTP/1.1",
        headers = U.idict(), body = (b"",), env = {}
      )
    )

  def test_init_kwds(self):
    x = H.Request(method = "POST", uri = "/foo",
                  headers = dict(Foo = "bar"), body = "<body>")
    self.assertEqual(
      dict(x.iteritems()),
      dict(
        method = "POST", uri = "/foo", version = "HTTP/1.1",
        headers = U.idict(Foo = "bar"), body = (b"<body>",), env = {}
      )
    )

  def test_init_dict(self):
    x = H.Request(dict(method = "POST", uri = "/foo",
                       headers = dict(Foo = "bar"), body = "<body>"))
    self.assertEqual(
      dict(x.iteritems()),
      dict(
        method = "POST", uri = "/foo", version = "HTTP/1.1",
        headers = U.idict(Foo = "bar"), body = (b"<body>",), env = {}
      )
    )

  def test_init_kwds_unknown(self):
    with self.assertRaisesRegexp(TypeError, "unknown keys"):
      H.Request(foo = 42)

  def test_init_kwds_and_data_no_mapping(self):
    with self.assertRaisesRegexp(TypeError, "must be a mapping"):
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
    self.assertEqual(x.body, (b"<body>",))

  def test_init_body_IStream(self):
    x = H.Request(body = S.IBytesStream("<body>"))
    self.assertIsInstance(x.body, type(x for x in []))
    self.assertEqual(b"".join(x.body), b"<body>")

  def test_force_body(self):
    x = H.Request(body = (x for x in "foo bar baz".split()))
    self.assertIsInstance(x.body, type(x for x in []))
    self.assertEqual(x.force_body, b"foobarbaz")
    self.assertIsInstance(x.body, tuple)
    self.assertEqual(x.body, (b"foobarbaz",))

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
    y = [("method", "GET"), ("uri", H.URI("/")),
         ("version", "HTTP/1.1"), ("headers", U.idict()),
         ("body", (b"<body>",)), ("env", {})]
    self.assertEqual(
      repr(x),
      "Request({})".format(
        ", ".join("{} = {}".format(k, repr(v)) for (k,v) in y)
      )
    )

  def test_unparse(self):
    x = H.Request(method = "POST", uri = "/foo",
                  headers = dict(Foo = "bar", X = "42"),
                  body = "<body>")
    self.assertRegexpMatches(
      U.STR(x.unparse()),
      "\\APOST /foo HTTP/1.1\r\n((Foo|X|Content-Length): "
      "(bar|42|6)\r\n)+\r\n<body>\\Z"
    )

  def test_unparse_chunked(self):
    x = H.Request(method = "POST", uri = "/foo",
                  headers = dict(Foo = "bar", X = "42"),
                  body = (x for x in ["<bo", "dy>"]))
    self.assertRegexpMatches(
      U.STR(x.unparse()),
      "\\APOST /foo HTTP/1.1\r\n((Foo|X|Transfer-Encoding): "
      "(bar|42|chunked)\r\n)+"
      "\r\n3\r\n<bo\r\n3\r\ndy>\r\n0\r\n\r\n\\Z"
    )
                                                                # }}}1

class Test_Response(unittest.TestCase):                         # {{{1

  # NB: the tests for Immutable and Request cover most of the common
  # functionality provided by Message

  def test_init_kwds(self):
    x = H.Response(status = 404, headers = dict(Foo = "bar"))
    self.assertEqual(
      dict(x.iteritems()),
      dict(
        version = "HTTP/1.1", status = 404, reason = "Not Found",
        headers = U.idict(Foo = "bar"), body = (b"",)
      )
    )

  def test_init_data_no_mapping_etc(self):
    with self.assertRaisesRegexp(TypeError, "must be a mapping, "
                                 "tuple, int, str, bytes, "
                                 "or iterable"):
      H.Response(3.14)

  def test_init_data_wrong_tuple(self):
    with self.assertRaisesRegexp(TypeError, "tuple data argument "
                                 "must have either 2 or 3 elements"):
      H.Response((1,2,3,4))

  def test_init_data_tuple(self):
    x = H.Response((404, dict(Foo = "bar"), "<body>"))
    self.assertEqual(
      dict(x.iteritems()),
      dict(
        version = "HTTP/1.1", status = 404, reason = "Not Found",
        headers = U.idict(Foo = "bar"), body = (b"<body>",)
      )
    )

  def test_init_data_int(self):
    x = H.Response(500)
    self.assertEqual(
      dict(x.iteritems()),
      dict(
        version = "HTTP/1.1", status = 500,
        reason = "Internal Server Error",
        headers = U.idict(), body = (b"",)
      )
    )

  def test_init_data_str(self):
    x = H.Response("<body>")
    self.assertEqual(
      dict(x.iteritems()),
      dict(
        version = "HTTP/1.1", status = 200, reason = "OK",
        headers = U.idict(), body = (b"<body>",)
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
      U.STR(x.unparse()),
      "\\AHTTP/1.1 200 OK\r\n((Foo|X|Content-Length): "
      "(bar|42|6)\r\n)+\r\n<body>\\Z"
    )
                                                                # }}}1

class Test_http(unittest.TestCase):                             # {{{1

  def test_requests_w_forced_bodies(self):
    r1  = "GET /foo HTTP/1.1\r\nContent-Length: 7\r\n\r\n<body1>"
    r2  = "GET /bar HTTP/1.1\r\nContent-Length: 7\r\n\r\n<body2>"
    self.assertEqual(
      list(H.force_bodies(H.requests(S.IBytesStream(r1 + r2)))),
      [
        H.Request(
          method = "GET", uri = "/foo",
          headers = { "Content-Length": "7" }, body = "<body1>"
        ),
        H.Request(
          method = "GET", uri = "/bar",
          headers = { "Content-Length": "7" }, body = "<body2>"
        )
      ]
    )

  def test_responses_w_forced_bodies(self):
    r1  = "HTTP/1.1 200 OK\r\nContent-Length: 6\r\n\r\n<body>"
    r2  = "HTTP/1.1 404 Not Found\r\n\r\n"
    r3  = "HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n" \
          "4\r\nfoo \r\n7\r\nbar baz\r\n0\r\n\r\n"
    self.assertEqual(
      list(H.force_bodies(H.responses(S.IBytesStream(r1+r2+r3)))),
      [
        H.Response(
          status = 200, reason = "OK",
          headers = { "Content-Length": "6" }, body = "<body>"
        ),
        H.Response(
          status = 404, reason = "Not Found", headers = {}, body = ""
        ),
        H.Response(
          headers = { "Transfer-Encoding": "chunked" },
          body = "foo bar baz"
        )
      ]
    )

  def test_request(self):
    x = H.Request(uri = "/foo")
    y = H.request(x)
    z = H.request(dict(uri = "/foo"))
    self.assertEqual(x, y)
    self.assertEqual(x, z)
    self.assertIs(x, y)
    self.assertIsNot(x, z)

  def test_response(self):
    x = H.Response("foo")
    y = H.response(x)
    z = H.response("foo")
    self.assertEqual(x, y)
    self.assertEqual(x, z)
    self.assertIs(x, y)
    self.assertIsNot(x, z)
                                                                # }}}1

# ...

if __name__ == "__main__":
  unittest.main()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
