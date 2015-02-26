.PHONY: test run repl sinatra curl clean

SHELL             = bash

LIBS              = TinyHTTPServer TinyHTTPServerUtils
CURL_PATH        ?= /

export PYTHONPATH = $(PWD)/lib:$(PWD)/test

test:
	python -m unittest $(patsubst %,%_test,$(LIBS))

run:
	python -m $(firstword $(LIBS))

repl:
	python -i -c 'import $(firstword $(LIBS))'

sinatra:
	ruby -rsinatra -e 'get("/") { "Hi!\n" }; get("/*") { request.env.inspect + "\n" }'

curl:
	curl -v "localhost:4567$(CURL_PATH)"

clean:
	shopt -s nullglob globstar; rm -f **/*.pyc
