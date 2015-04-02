# --                                                            ; {{{1
#
# File        : httpony/util.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-04-01
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

"""utilities like case-insensitive dict and Immutable base class"""

import collections
import sys

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

  if sys.version_info.major != 2:
    def iteritems(self):
      return (x for x in self.items())

  # lowercase keys
  def iteritems_lower(self):
    return ((k, v[1]) for k, v in iteritems(self._data))

  if sys.version_info.major != 2:
    def items_lower(self):
      return list(self.iteritems_lower())

  def copy(self):
    return type(self)(self._data.values())

  # ... and we also need to override these

  def __eq__(self, rhs):
    if not isinstance(rhs, collections.Mapping): return NotImplemented
    if not isinstance(rhs, idict): rhs = idict(rhs)
    return dict(self.iteritems_lower()) == dict(rhs.iteritems_lower())

  def __lt__(self, rhs):
    if not isinstance(rhs, collections.Mapping): return NotImplemented
    if not isinstance(rhs, idict): rhs = idict(rhs)
    return sorted(self.iteritems_lower()) < \
           sorted(rhs.iteritems_lower())

  def __le__(self, rhs):
    if not isinstance(rhs, collections.Mapping): return NotImplemented
    if not isinstance(rhs, idict): rhs = idict(rhs)
    return sorted(self.iteritems_lower()) <= \
           sorted(rhs.iteritems_lower())

  def __gt__(self, rhs):
    if not isinstance(rhs, collections.Mapping): return NotImplemented
    if not isinstance(rhs, idict): rhs = idict(rhs)
    return sorted(self.iteritems_lower()) > \
           sorted(rhs.iteritems_lower())

  def __ge__(self, rhs):
    if not isinstance(rhs, collections.Mapping): return NotImplemented
    if not isinstance(rhs, idict): rhs = idict(rhs)
    return sorted(self.iteritems_lower()) >= \
           sorted(rhs.iteritems_lower())

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

  @property
  def ___slots(self):
    return [x for x in self.__slots__ if not x.startswith("_")]

  def __init__(self, data = None, **kw):
    x = data if data is not None else {}; x.update(kw)
    ks = set(x.keys()); ss = set(self.___slots)
    for k in self.___slots:
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
    if k in self.___slots:
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
    return ((k, getattr(self, k)) for k in self.___slots)

  if sys.version_info.major == 2:
    def items(self):
      return list(self.iteritems())
  else:
    def items(self):
      return self.iteritems()

  def __eq__(self, rhs):
    if not isinstance(rhs, type(self)): return NotImplemented
    return dict(self.iteritems()) == dict(rhs.iteritems())

  def __lt__(self, rhs):
    if not isinstance(rhs, type(self)): return NotImplemented
    return sorted(self.iteritems()) < sorted(rhs.iteritems())

  def __le__(self, rhs):
    if not isinstance(rhs, type(self)): return NotImplemented
    return sorted(self.iteritems()) <= sorted(rhs.iteritems())

  def __gt__(self, rhs):
    if not isinstance(rhs, type(self)): return NotImplemented
    return sorted(self.iteritems()) > sorted(rhs.iteritems())

  def __ge__(self, rhs):
    if not isinstance(rhs, type(self)): return NotImplemented
    return sorted(self.iteritems()) >= sorted(rhs.iteritems())

  def __repr__(self):
    return '{}({})'.format(
      self.__class__.__name__,
      ", ".join("{} = {}".format(k, repr(v))
                for (k,v) in self.iteritems())
    )
                                                                # }}}1

def escape_html(s, quote = True):
  """escape HTML"""
  s = s.replace("&", "&amp;").replace("<", "&lt;") \
       .replace(">", "&gt;")
  if quote: s = s.replace('"', "&quot;").replace("'", "&apos;")
  return s

if sys.version_info.major == 2:
  def iteritems(x):
    """python2's iteritems()"""
    return x.iteritems()
else:
  def iteritems(x):
    """python3's items()"""
    return x.items()

if sys.version_info.major == 2:
  def STR(x):
    """-> str"""
    return str(x)
  def BY(x):
    """-> bytes"""
    return bytes(x)
else:
  def STR(x):
    """-> str"""
    if isinstance(x, str): return x
    return str(x, encoding = "utf8")
  def BY(x):
    """-> bytes"""
    if isinstance(x, bytes): return x
    return bytes(x, encoding = "utf8")

# ...

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
