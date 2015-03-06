.PHONY: test test_v repl run serve_docs shell clean sinatra curl

SHELL       = bash

LIB         = httpony
RUN         = server

CURL_PATH  ?= /
PYDOC_PORT ?= 1234

export PYTHONPATH = $(PWD)/lib:$(PWD)/test

test:
	python -m unittest discover -s test -p '*_spec.py'

test_v:
	python -m unittest discover -s test -p '*_spec.py' -v

repl:
	python -i -c 'from $(LIB) import *'

run:
	python -m $(LIB).$(RUN)

serve_docs:
	pydoc -p $(PYDOC_PORT)

shell:
	bash

clean:
	shopt -s nullglob globstar; rm -f **/*.pyc

sinatra:
	ruby -rsinatra -e 'get("/") { "Hi!\n" }; \
	  get("/*") { request.env.inspect + "\n" }; \
	  post("/*") { request.body.read() }'

curl:
	curl -v "localhost:4567$(CURL_PATH)"
