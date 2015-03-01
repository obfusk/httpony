.PHONY: repl clean

SHELL = bash
LIB   = httpony

export PYTHONPATH = $(PWD)/lib:$(PWD)/test

repl:
	python -i -c 'from $(LIB) import *'

clean:
	shopt -s nullglob globstar; rm -f **/*.pyc
