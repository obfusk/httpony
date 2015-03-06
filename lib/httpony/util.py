# --                                                            ; {{{1
#
# File        : httpony/util.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-06
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

"""utilities like case-insensitive dict and Immutable base class"""

import collections

class idict(collections.MutableMapping):                        # {{{1

  """case-insensitive dict"""

  def __init__(self, data = None, **kw):
    self._data = {}
    if data is not None: self.update(data)
    self.update(**kw)

  # implement abstract methods ...

  def __getitem__(self, k):
    return self._data[k.lower()][1]

  def __setitem__(self, k, v):
    self._data[k.lower()] = (k, v)

  def __delitem__(self, k):
    del self._data[k.lower()]

  # original keys
  def __iter__(self):
    return (k for k, v in self._data.values())

  def __len__(self):
    return len(self._data)

  # ... and these are nice to have ...

  # lowercase keys
  def iteritems_lower(self):
    return ((k, v[1]) for k, v in self._data.iteritems())

  def copy(self):
    return type(self)(self._data.values())

  # ... and we also need to override these

  def __eq__(self, rhs):
    if not isinstance(rhs, collections.Mapping):
      return NotImplemented
    if not isinstance(rhs, idict):
      rhs = idict(rhs)
    return dict(self.iteritems_lower()) == dict(rhs.iteritems_lower())

  def __cmp__(self, rhs):
    if not isinstance(rhs, collections.Mapping):
      return NotImplemented
    if not isinstance(rhs, idict):
      rhs = idict(rhs)
    return dict(self.iteritems_lower()) \
      .__cmp__(dict(rhs.iteritems_lower()))

  def __repr__(self):
    return '{}({})'.format(
      self.__class__.__name__,
      repr(dict(self.iteritems()))
    )
                                                                # }}}1

class Immutable(object):                                        # {{{1

  """immutable base class"""

  __slots__ = []

  args_are_mandatory = False

  def __init__(self, data = None, **kw):
    x = data if data is not None else {}; x.update(kw)
    ks = set(x.keys()); ss = set(self.__slots__)
    for k in self.__slots__:
      if k in x:
        self._Immutable___set(k, x[k]); del x[k]
      else:
        self._Immutable___set(k, None)
    if len(x):
      raise TypeError("unknown keys: {}".format(", ".join(x.keys())))
    if self.args_are_mandatory and ks != ss:
      raise TypeError("missing keys: {}".format(", ".join(ss - ks)))

  def ___set(self, k, v):
    super(Immutable, self).__setattr__(k, v)

  def __setattr__(self, k, v):
    if k in self.__slots__:
      raise AttributeError(
        "'{}' object attribute '{}' is read-only".format(
          self.__class__.__name__, k
        )
      )
    else:
      raise AttributeError(
        "'{}' object has no attribute '{}'".format(
          self.__class__.__name__, k
        )
      )

  def copy(self, **kw):
    return type(self)(dict(self.iteritems()), **kw)

  def iteritems(self):
    return ((k, getattr(self, k)) for k in self.__slots__)

  def items(self):
    return list(self.iteritems())

  def __eq__(self, rhs):
    if not isinstance(rhs, type(self)):
      return NotImplemented
    return dict(self.iteritems()) == dict(rhs.iteritems())

  def __cmp__(self, rhs):
    if not isinstance(rhs, type(self)):
      return NotImplemented
    return dict(self.iteritems()).__cmp__(dict(rhs.iteritems()))

  def __repr__(self):
    return '{}({})'.format(
      self.__class__.__name__,
      ", ".join("{} = {}".format(k, repr(v))
                for (k,v) in self.iteritems())
    )
                                                                # }}}1

# ...

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
