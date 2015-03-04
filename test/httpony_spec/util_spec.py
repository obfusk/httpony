# --                                                            ; {{{1
#
# File        : util_spec.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-04
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

import httpony.util as U
import unittest

class Test_util(unittest.TestCase):                             # {{{1

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
    self.assertEqual(x.values(), [])

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

  def test_repr(self):
    x = U.idict(x = 42)
    self.assertEqual(str(x), "idict({'x': 42})")
                                                                # }}}1

# ...

if __name__ == "__main__":
  unittest.main()

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
