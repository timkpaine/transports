.DEFAULT_GOAL := help
.PHONY: build develop clean help lint fix format tests test

UNAME := $(shell uname)
ifeq ($(UNAME), Darwin)
	_CP_COMMAND := cp target/debug/libtransports.dylib transports/transports.abi3.so
else
	_CP_COMMAND := cp target/debug/libtransports.so transports/transports.abi3.so
endif

build:  ## build the library
	maturin build

build-sdist:  ## build the sdist
	maturin sdist

dev: build  ## lightweight in-place build
	$(_CP_COMMAND)

develop:  ## build the library for development
	pip install -U build maturin setuptools twine wheel
	pip install -e .[develop]

lint:  ## run linters
	python -m isort transports --check
	python -m ruff check transports

fix:  ## run autofixers
	python -m isort transports
	python -m ruff format transports

format: fix

tests:  ## run tests
	python -m pytest -v transports/tests --junitxml=junit.xml --cov=transports --cov-branch --cov-fail-under=65 --cov-report term-missing --cov-report xml

test: tests

checks:  ## run checks
	# python -m check_manifest

clean:  ## clean the project
	git clean -fdx

dist: clean build build-sdist  ## create dists
	python -m twine check target/wheels/*

publish: dist  ## dist to pypi
	python -m twine upload target/wheels/* --skip-existing

# Thanks to Francoise at marmelab.com for this
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

print-%:
	@echo '$*=$($*)'
