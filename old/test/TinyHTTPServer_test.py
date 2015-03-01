# --                                                            ; {{{1
#
# File        : TinyHTTPServer_test.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-02-26
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

import TinyHTTPServer as T
import TinyHTTPServerUtils as U
import unittest

# TODO
class Test_TinyHTTPServer_Server(unittest.TestCase):
  pass


class Test_TinyHTTPServer_Client(unittest.TestCase):

  def setUp(self):
    self.client = T.Client()

  def test_default_headers(self):
    x = U.lower_keys(self.client.default_headers())
    self.assertIsInstance(x, dict)
    self.assertEqual(x["user-agent"], T.DEFAULT_AGENT)

  def test_request(self):
    pass

  # NB: uses socket
  def test_make_request(self):
    pass

  # NB: uses socket
  def test_get(self):
    pass

  # ...


class Test_TinyHTTPServer_FakeClient(unittest.TestCase):

  def setUp(self):
    self.client = T.FakeClient()

  # NB: uses fake socket
  def test_make_request(self):
    pass

  # NB: uses fake socket
  def test_get(self):
    pass

  # ...


if __name__ == "__main__":
  unittest.main()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
