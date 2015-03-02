# --                                                            ; {{{1
#
# File        : stream_spec.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-01
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

import httpony.stream as S
import unittest

class IStringStream_(S.IStringStream):

  def readlines_orig(self):
    return S.IStream.readlines(self)


class Test_IStringStream(unittest.TestCase):

  def test_read(self):
    s = S.IStringStream("foo bar baz")
    y = "foo bar baz"
    self.assertEqual(s.read(), y)

  def test_read_n(self):
    s = S.IStringStream("foo bar baz")
    y = "foo bar"
    self.assertEqual(s.read(7), y)

  def test_readline(self):
    s = S.IStringStream("foo\nbar\nbaz\n")
    y = "foo\n"
    z = "bar\n"
    self.assertEqual(s.readline(), y)
    self.assertEqual(s.readline(), z)

  def test_readlines(self):
    s = S.IStringStream("foo\nbar\nbaz\n")
    y = ["foo\n", "bar\n", "baz\n"]
    self.assertEqual(list(s), y)

  def test_readlines_from_istream(self):
    s = IStringStream_("foo\nbar\nbaz\n")
    y = ["foo\n", "bar\n", "baz\n"]
    self.assertEqual(list(s.readlines_orig()), y)

  def test_readchunks(self):
    s = S.IStringStream("foo\nbar\nbaz\n")
    y = ["foo\nbar\n", "baz\n"]
    self.assertEqual(list(s.readchunks(8)), y)


class Test_OStringStream(unittest.TestCase):

  def test_write(self):
    s = S.OStringStream()
    y = "foo bar"
    z = "baz qux"
    s.write(y)
    self.assertEqual(s.getvalue(), y)
    s.write(z)
    self.assertEqual(s.getvalue(), y + z)


class Test_stream(unittest.TestCase):

  def test_interact(self):
    si = S.IStringStream("foo\nbar\nbaz\n")
    so = S.OStringStream()
    def f(xs):
      for line in S.stripped_lines(xs):
        yield line.upper()[::-1] + "\n"
    S.interact(si, so, f)
    self.assertEqual(so.getvalue(), "OOF\nRAB\nZAB\n")

  def test_stripped_lines(self):
    x = "foo\nbar\r\nbaz\n".splitlines()
    y = ["foo", "bar", "baz"]
    self.assertEqual(list(S.stripped_lines(x)), y)


# ...


if __name__ == "__main__":
  unittest.main()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
