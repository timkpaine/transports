.DEFAULT_GOAL := help
.PHONY: build develop clean help lint fix format tests test coverage

build:  ## build the library
	maturin build

develop:  ## build the library for development
	pip install -U build maturin setuptools twine wheel
	pip install -e .[develop]

lint:  ## run linters
	python -m ruff transports

fix:  ## run autofixers
	python -m ruff transports --fix
format: fix

tests:  ## run tests
	python -m pytest -v transports/tests --junitxml=junit.xml
tests: test

coverage:
	python -m pytest -v transports/tests --junitxml=junit.xml --cov=transports --cov-branch --cov-fail-under=80 --cov-report term-missing

checks:  ## run checks
	# python -m check_manifest

clean:  ## clean the project
	git clean -fdx

# Thanks to Francoise at marmelab.com for this
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

print-%:
	@echo '$*=$($*)'
