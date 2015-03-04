# --                                                            ; {{{1
#
# File        : httpony/util.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-03-04
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

import collections

class idict(collections.MutableMapping):                        # {{{1

  """case-insensitive dict"""

  def __init__(self, data=None, **kw):
    self._data = {}
    if data != None: self.update(data)
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
    return idict(self._data.values())

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

# ...

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
