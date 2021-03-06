[]: {{{1

    File        : README.md
    Maintainer  : Felix C. Stegerman <flx@obfusk.net>
    Date        : 2015-03-09

    Copyright   : Copyright (C) 2015  Felix C. Stegerman
    Version     : v0.0.1

[]: }}}1

<!-- badge? -->

## Description
[]: {{{1

  HTTPony - HTTP server/client/dsl

  I wanted ~~a pony~~ to build an HTTP server/client/dsl.

  ...

[]: }}}1

## Specs & Docs

```bash
$ make test
$ make coverage
```

## TODO

  * httpony.server
  * chunked, persistent, redirect, %-enc, ...
  * etag, context, static, env, ...
  * docs
  * error handling (?!)
  * more specs (?)
  * optimisations (?)
  * httpony.machine (?)
  * httpony.middleware (?)
  * max body & headers (?)
  * ...

### Mostly done

  * httpony.client
  * httpony.handler
  * httpony.http
  * httpony.stream
  * httpony.util

## License

  LGPLv3+ [1].

## References

  [1] GNU Lesser General Public License, version 3
  --- https://www.gnu.org/licenses/lgpl-3.0.html

[]: ! ( vim: set tw=70 sw=2 sts=2 et fdm=marker : )
