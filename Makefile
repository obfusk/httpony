.PHONY: test test_v coverage repl run
.PHONY: serve_docs shell clean sinatra curl

SHELL       = bash

LIB         = httpony
RUN         = server

CURL_PATH  ?= /
PYDOC_PORT ?= 1234

export PYTHONPATH = $(PWD)/lib:$(PWD)/test

test:
	python test.py

test_v:
	python test.py 2

coverage:
	python-coverage run test.py
	python-coverage html

repl:
	rlwrap --always-readline python -i -c 'from $(LIB) import *'

run:
	python -m $(LIB).$(RUN)

serve_docs:
	pydoc -p $(PYDOC_PORT)

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
