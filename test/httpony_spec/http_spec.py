# --                                                            ; {{{1
#
# File        : http_spec.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-01
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

import httpony.http as H
import httpony.stream as S
import unittest

class Test_http(unittest.TestCase):

  def test_requests_w_evaluated_bodies(self):
    r1  = "GET /foo HTTP/1.1\r\nContent-length: 7\r\n\r\n<body1>"
    r2  = "GET /bar HTTP/1.1\r\nContent-length: 7\r\n\r\n<body2>"
    self.assertEqual(
      list(H.evaluate_bodies(H.requests(S.IStringStream(r1 + r2)))),
      [
        dict(
          method = "GET", uri = "/foo", version = "HTTP/1.1",
          headers = { "content-length": "7" }, body = "<body1>"
        ),
        dict(
          method = "GET", uri = "/bar", version = "HTTP/1.1",
          headers = { "content-length": "7" }, body = "<body2>"
        )
      ]
    )

  def test_responses_w_evaluated_bodies(self):
    r1  = "HTTP/1.1 200 OK\r\nContent-length: 6\r\n\r\n<body>"
    r2  = "HTTP/1.1 404 Not Found\r\n\r\n"
    self.assertEqual(
      list(H.evaluate_bodies(H.responses(S.IStringStream(r1 + r2)))),
      [
        dict(
          version = "HTTP/1.1", status = 200, reason = "OK",
          headers = { "content-length": "6" }, body = "<body>"
        ),
        dict(
          version = "HTTP/1.1", status = 404, reason = "Not Found",
          headers = {}, body = ""
        )
      ]
    )


# ...


if __name__ == "__main__":
  unittest.main()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
