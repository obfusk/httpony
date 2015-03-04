# --                                                            ; {{{1
#
# File        : stream_spec.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-04
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

import httpony.stream as S
import unittest

class IStringStream_(S.IStringStream):                          # {{{1

  def readlines_orig(self):
    return S.IStream.readlines(self)
                                                                # }}}1

class Test_IStringStream(unittest.TestCase):                    # {{{1

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

  def test_split_chunks(self):
    s     = S.IStringStream("foo\nbar\nbaz\n")
    t, d  = s.split(10)
    y     = ["fo", "o\n", "ba", "r\n", "ba"]
    z     = "z\n"
    self.assertEqual(list(t.readchunks(2)), y)
    self.assertEqual(d.read(), z)

  def test_split_chunks_forced(self):
    s     = S.IStringStream("foo\nbar\nbaz\n")
    t, d  = s.split(10)
    y     = ["fo", "o\n", "ba", "r\n", "ba"]
    z     = "z\n"
    self.assertEqual(d.read(), z)
    self.assertEqual(list(t.readchunks(2)), y)

  def test_split_readline(self):
    s     = S.IStringStream("foo\nbar\nbaz\n")
    t, d  = s.split(10, 1)  # test bufsize too
    y     = ["foo\n", "bar\n", "ba"]
    z     = "z\n"
    self.assertEqual(t.readline(), y[0])
    self.assertEqual(t.readline(), y[1])
    self.assertEqual(d.readline(), z)
    self.assertEqual(t.readline(), y[2])

  def test_split_readlines(self):
    s     = S.IStringStream("foo\nbar\nbaz\n")
    t, d  = s.split(10)
    y     = ["foo\n", "bar\n", "ba"]
    z     = ["z\n"]
    self.assertEqual(list(t), y)
    self.assertEqual(list(d), z)

  # ...
                                                                # }}}1

class Test_OStringStream(unittest.TestCase):                    # {{{1

  def test_write(self):
    s = S.OStringStream()
    y = "foo bar"
    z = "baz qux"
    s.write(y)
    self.assertEqual(s.getvalue(), y)
    s.write(z)
    self.assertEqual(s.getvalue(), y + z)
                                                                # }}}1

class Test_stream(unittest.TestCase):                           # {{{1

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

  def test_unstripped_lines(self):
    x = "foo bar baz".split()
    y = ["foo\r\n", "bar\r\n", "baz\r\n"]
    self.assertEqual(list(S.unstripped_lines(x)), y)
                                                                # }}}1

# ...

if __name__ == "__main__":
  unittest.main()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
