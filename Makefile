.PHONY: test test_v coverage repl run
.PHONY: serve_docs shell clean sinatra curl

SHELL       = bash

LIB         = httpony
RUN         = server

PY         ?= python$(PYVSN)
CURL_PATH  ?= /
PYDOC_PORT ?= 1234

export PYTHONPATH = $(PWD)/lib:$(PWD)/test

test:
	$(PY) test.py

test_v:
	$(PY) test.py 2

coverage:
	$(PY)-coverage run test.py
	$(PY)-coverage html

repl:
	rlwrap --always-readline $(PY) -i -c 'from $(LIB) import *'

run:
	$(PY) -m $(LIB).$(RUN)

serve_docs:
	pydoc$(PYVSN) -p $(PYDOC_PORT)

shell:
	bash

clean:
	shopt -s nullglob globstar; rm -f **/*.pyc
	rm -fr .coverage htmlcov/

sinatra:
	ruby -rsinatra -e 'get("/") { "Hi!\n" }; \
	  get("/*") { request.env.inspect + "\n" }; \
	  post("/*") { request.body.read() }'

curl:
	curl -v "localhost:4567$(CURL_PATH)"
