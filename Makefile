.PHONY: test run repl clean sinatra curl

SHELL       = bash

LIB         = httpony
RUN         = server

CURL_PATH  ?= /

export PYTHONPATH = $(PWD)/lib:$(PWD)/test

test:
	python -m unittest discover -s test -p '*_spec.py'

test_v:
	python -m unittest discover -s test -p '*_spec.py' -v

run:
	python -m $(LIB).$(RUN)

repl:
	python -i -c 'from $(LIB) import *'

clean:
	shopt -s nullglob globstar; rm -f **/*.pyc

sinatra:
	ruby -rsinatra -e 'get("/") { "Hi!\n" }; \
	  get("/*") { request.env.inspect + "\n" }; \
	  post("/*") { request.body.read() }'

curl:
	curl -v "localhost:4567$(CURL_PATH)"
