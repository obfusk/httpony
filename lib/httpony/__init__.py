# --                                                            ; {{{1
#
# File        : httpony/__init__.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-04-01
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

"""HTTP server/client/dsl"""

__all__     = "client handler http server stream util".split()
__version__ = '0.0.1'

DEFAULT_USER_AGENT  = "httpony.client/{}".format(__version__)
DEFAULT_SERVER      = "httpony.server/{}".format(__version__)

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
