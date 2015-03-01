.PHONY: test run repl clean sinatra curl

SHELL       = bash

LIB         = httpony
SUBLIBS     = client handler request response server stream
RUN         = server
TESTS       = $(patsubst %,$(LIB)_spec.%_spec,$(SUBLIBS))

CURL_PATH  ?= /

export PYTHONPATH = $(PWD)/lib:$(PWD)/test

test:
	python -m unittest $(TESTS)

test_v:
	python -m unittest -v $(TESTS)

run:
	python -m $(LIB).$(RUN)

repl:
	python -i -c 'from $(LIB) import *'

clean:
	shopt -s nullglob globstar; rm -f **/*.pyc

sinatra:
	ruby -rsinatra -e 'get("/") { "Hi!\n" }; \
	  get("/*") { request.env.inspect + "\n" }'

curl:
	curl -v "localhost:4567$(CURL_PATH)"
