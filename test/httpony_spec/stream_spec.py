# --                                                            ; {{{1
#
# File        : stream_spec.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-09
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

import httpony.stream as S
import unittest

def chunker(si):
  while True:
    n = int(si.readline())
    if n == 0: break
    yield si.split(n)[0].read()
    si.readline()

class IBytesStream_(S.IBytesStream):                            # {{{1

  def readlines_orig(self):
    return S.IStream.readlines(self)
                                                                # }}}1

class Test_IBytesStrean(unittest.TestCase):                     # {{{1

  def test_read(self):
    s = S.IBytesStream("foo bar baz")
    y = b"foo bar baz"
    self.assertEqual(s.read(), y)

  def test_read_n(self):
    s = S.IBytesStream("foo bar baz")
    y = b"foo bar"
    self.assertEqual(s.read(7), y)

  def test_readline(self):
    s = S.IBytesStream("foo\nbar\nbaz\n")
    y = b"foo\n"
    z = b"bar\n"
    self.assertEqual(s.readline(), y)
    self.assertEqual(s.readline(), z)

  def test_readlines(self):
    s = S.IBytesStream("foo\nbar\nbaz\n")
    y = [b"foo\n", b"bar\n", b"baz\n"]
    self.assertEqual(list(s), y)

  def test_readlines_from_istream(self):
    s = IBytesStream_("foo\nbar\nbaz\n")
    y = [b"foo\n", b"bar\n", b"baz\n"]
    self.assertEqual(list(s.readlines_orig()), y)

  def test_readchunks(self):
    s = S.IBytesStream("foo\nbar\nbaz\n")
    y = [b"foo\nbar\n", b"baz\n"]
    self.assertEqual(list(s.readchunks(8)), y)

  def test_split_chunks(self):
    s     = S.IBytesStream("foo\nbar\nbaz\n")
    t, d  = s.split(10)
    y     = [b"fo", b"o\n", b"ba", b"r\n", b"ba"]
    z     = b"z\n"
    self.assertEqual(list(t.readchunks(2)), y)
    self.assertEqual(d.read(), z)

  def test_split_chunks_forced(self):
    s     = S.IBytesStream("foo\nbar\nbaz\n")
    t, d  = s.split(10)
    y     = [b"fo", b"o\n", b"ba", b"r\n", b"ba"]
    z     = b"z\n"
    self.assertEqual(d.read(), z)
    self.assertEqual(list(t.readchunks(2)), y)

  def test_split_readline(self):
    s     = S.IBytesStream("foo\nbar\nbaz\n")
    t, d  = s.split(10, 1)  # test bufsize too
    y     = [b"foo\n", b"bar\n", b"ba"]
    z     = b"z\n"
    self.assertEqual(t.readline(), y[0])
    self.assertEqual(t.readline(), y[1])
    self.assertEqual(d.readline(), z)
    self.assertEqual(t.readline(), y[2])

  def test_split_readlines(self):
    s     = S.IBytesStream("foo\nbar\nbaz\n")
    t, d  = s.split(10)
    y     = [b"foo\n", b"bar\n", b"ba"]
    z     = [b"z\n"]
    self.assertEqual(list(t), y)
    self.assertEqual(list(d), z)

  def test_splitchunked(self):
    s     = S.IBytesStream("3\nfoo\n7\nbar\nbaz\n0\nqux")
    t, d  = s.splitchunked(chunker)
    self.assertEqual(t.read(), b"foobar\nbaz")
    self.assertEqual(d.read(), b"qux")

  def test_splitchunked_forced(self):
    s     = S.IBytesStream("3\nfoo\n7\nbar\nbaz\n0\nqux")
    t, d  = s.splitchunked(chunker)
    self.assertEqual(d.read(), b"qux")
    self.assertEqual(t.read(), b"foobar\nbaz")

  def test_splitchunked_chunks(self):
    s     = S.IBytesStream("3\nfoo\n7\nbar\nbaz\n0\nqux")
    t, d  = s.splitchunked(chunker)
    self.assertEqual(list(t.readchunks(2)),
                     [b"fo", b"ob", b"ar", b"\nb", b"az"])
    self.assertEqual(d.read(), b"qux")

  def test_splitchunked_readline(self):
    s     = S.IBytesStream("3\nfoo\n7\nbar\nbaz\n0\nqux")
    t, d  = s.splitchunked(chunker, 1)  # test bufsize too
    y     = [b"foobar\n", b"baz"]
    z     = b"qux"
    self.assertEqual(t.readline(), y[0])
    self.assertEqual(d.readline(), z)
    self.assertEqual(t.readline(), y[1])

  def test_splitchunked_readlines(self):
    s     = S.IBytesStream("3\nfoo\n7\nbar\nbaz\n0\nqux")
    t, d  = s.splitchunked(chunker)
    y     = [b"foobar\n", b"baz"]
    z     = [b"qux"]
    self.assertEqual(list(t), y)
    self.assertEqual(list(d), z)

  # ...
                                                                # }}}1

class Test_OBytesStream(unittest.TestCase):                     # {{{1

  def test_write(self):
    s = S.OBytesStream()
    y = b"foo bar"
    z = b"baz qux"
    s.write(y)
    self.assertEqual(s.getvalue(), y)
    s.write(z)
    self.assertEqual(s.getvalue(), y + z)
                                                                # }}}1

class Test_stream(unittest.TestCase):                           # {{{1

  def test_ifile_stream(self):
    si = S.ifile_stream("/dev/null")
    self.assertEqual(si.length(), 0)
                                                                # }}}1

# ...

if __name__ == "__main__":
  unittest.main()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
