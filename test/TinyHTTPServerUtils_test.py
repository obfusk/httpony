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

  def test_headers(self):
    x = { 'User-Agent': 'foo/1.2', 'Foo': 'Bar' }
    y = { 'user-agent': 'foo/1.2', 'foo': 'Bar' }
    self.assertEqual(U.headers(x), y)

  # ...


if __name__ == '__main__':
  unittest.main()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
