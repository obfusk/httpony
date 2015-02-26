# --                                                            ; {{{1
#
# File        : TinyHTTPServerUtils.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2015-02-26
#
# Copyright   : Copyright (C) 2015  Felix C. Stegerman
# Licence     : LGPLv3+
#
# --                                                            ; }}}1

CRLF = "\r\n"

def crlf(xs):
  """joins list of lines (w/o newline) w/ CRLF"""
  return ''.join(map(lambda x: x + CRLF, xs))

def deindent(x, n):
  """creates list of n-char-deindented lines (minus first and last);
  for pseudo-heredocs"""
  return map(lambda x: x[n:], x.splitlines()[1:-1])

def headers(x):
  """lowercases keys of dict; useful for headers"""
  return dict(((k.lower(), v) for (k, v) in x.items()))

# TODO: look at spec, handle errors
def parse_headers_and_body(body):
  """parse headers + body into dict w/ headers + body"""
  hs = {}
  while True:
    x = body.split(CRLF, 1)
    if len(x) != 2:
      body = x[0]; break
    h, body = x
    if h == '': break
    k, v = h.split(':', 1); hs[k] = v.strip()
  return dict(headers = hs, body = body)

# TODO
def parse_request(body):
  pass

def parse_response(body):
  """turn raw response into dict w/ headers, body, status, etc."""
  status_line, body = body.split(CRLF, 1)
  http_version, status_code, reason = status_line.split(' ', 2)
  return parse_headers_and_body(body).update(
    version = http_version.upper(), status = int(status_code),
    reason = reason
  )

# ...

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
