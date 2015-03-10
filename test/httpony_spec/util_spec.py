# --                                                            ; {{{1
#
# File        : util_spec.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-09
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

import httpony.util as U
import unittest

class Test_idict(unittest.TestCase):                            # {{{1

  def test_get(self):
    x = U.idict(Foo = 42, Bar = 37)
    self.assertEqual(x['Foo'], 42)
    self.assertEqual(x['foo'], 42)
    self.assertEqual(x['fOO'], 42)
    self.assertEqual(x['Bar'], 37)

  def test_set(self):
    x = U.idict(); x['Foo'] = 42; x['Bar'] = 37
    self.assertEqual(x['Foo'], 42)
    self.assertEqual(x['foo'], 42)
    self.assertEqual(x['fOO'], 42)
    self.assertEqual(x['Bar'], 37)

  def test_del(self):
    x = U.idict(Foo = 42); del x['foo']
    self.assertEqual(list(x.values()), [])

  def test_iter(self):
    x = U.idict(Foo = 42, Bar = 37)
    y = iter(x)
    self.assertIsInstance(y, type(x for x in []))
    self.assertEqual(sorted(y), ["Bar", "Foo"])

  def test_len(self):
    x = U.idict()
    self.assertEqual(len(x), 0)
    x['Foo'] = 42; x['Bar'] = 37
    self.assertEqual(len(x), 2)
    del x['foo']
    self.assertEqual(len(x), 1)

  def test_iteritems(self):
    x = U.idict(Foo = 42, Bar = 37)
    y = x.iteritems()
    self.assertIsInstance(y, type(x for x in []))
    self.assertEqual(sorted(y), [("Bar", 37), ("Foo", 42)])

  def test_iteritems_lower(self):
    x = U.idict(Foo = 42, Bar = 37)
    y = x.iteritems_lower()
    self.assertIsInstance(y, type(x for x in []))
    self.assertEqual(sorted(y), [("bar", 37), ("foo", 42)])

  def test_copy(self):
    x = U.idict(Foo = 42, Bar = 37)
    y = x.copy()
    self.assertIsInstance(y, U.idict)
    self.assertEqual(x, y)
    del x['foo']
    self.assertNotEqual(x, y)

  def test_eq(self):
    x = U.idict(Foo = 42, Bar = 37)
    y = U.idict(Foo = 42, Bar = 37)
    z = U.idict(Foo = 42, Bar = 99)
    self.assertEqual(x, y)
    self.assertNotEqual(x, z)

  def test_cmp(self):
    x = U.idict(Foo = 42, Bar = 37)
    y = U.idict(Foo = 42, Bar = 37)
    z = U.idict(Foo = 42, Bar = 99)
    self.assertGreater(z, x)
    self.assertGreaterEqual(z, y)
    self.assertLess(y, z)
    self.assertLessEqual(x, y)

  def test_repr(self):
    x = U.idict(x = 42)
    self.assertEqual(str(x), "idict({'x': 42})")
                                                                # }}}1

class X(U.Immutable):
  __slots__ = "foo bar baz".split()

class Y(X):
  args_are_mandatory = True

class Test_Immutable(unittest.TestCase):                        # {{{1

  def test_init_ok(self):
    x = X(foo = 42)
    self.assertEqual(x.foo, 42)

  def test_init_unknown(self):
    with self.assertRaisesRegexp(TypeError, "unknown keys"):
      X(spam = 99)

  def test_init_missing(self):
    with self.assertRaisesRegexp(TypeError, "missing keys"):
      Y(foo = 42)

  def test_no_setattr(self):
    x = X()
    with self.assertRaisesRegexp(AttributeError, "'X' object " +
                                 "attribute 'foo' is read-only"):
      x.foo = 99

  def test_no_setattr_new(self):
    x = X()
    with self.assertRaisesRegexp(AttributeError, "'X' object " +
                                 "has no attribute 'spam'"):
      x.spam = 99

  def test_copy(self):
    x = X(foo = 42, bar = 37)
    y = x.copy()
    z = x.copy(baz = 99)
    self.assertEqual(x, y)
    self.assertNotEqual(x, z)
    self.assertEqual(x.baz, None)
    self.assertEqual(z.baz, 99)

  def test_iteritems(self):
    x = X(foo = 42, bar = 37)
    self.assertEqual(dict(x.iteritems()),
                     dict(foo = 42, bar = 37, baz = None))

  def test_items(self):
    x = X(foo = 42, bar = 37)
    self.assertEqual(list(x.items()),
                     [("foo", 42), ("bar", 37), ("baz", None)])

  def test_eq(self):
    x = X(foo = "foo")
    y = X(foo = "bar")
    self.assertEqual(x, x)
    self.assertNotEqual(x, y)

  def test_cmp(self):
    x = X(foo = "foo")
    y = X(foo = "bar")
    self.assertGreater(x, y)
    self.assertGreaterEqual(x, y)
    self.assertGreaterEqual(x, x)
    self.assertLess(y, x)
    self.assertLessEqual(y, x)

  def test_repr(self):
    x = X(foo = 42, bar = "hi!")
    y = [("foo", 42), ("bar", "hi!"), ("baz", None)]
    self.assertEqual(
      repr(x),
      "X({})".format(
        ", ".join("{} = {}".format(k, repr(v)) for (k,v) in y)
      )
    )
                                                                # }}}1

# ...

if __name__ == "__main__":
  unittest.main()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
