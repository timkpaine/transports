.DEFAULT_GOAL := help
.PHONY: dev build lint fix check tests coverage develop test format checks help

dev:  ## Install required dev dependencies
	rustup component add rustfmt
	rustup component add clippy
	cargo install cargo-nextest 
	cargo install cargo-llvm-cov
	cargo install -f wasm-bindgen-cli
	rustup target add wasm32-unknown-unknown

build:  ## Build release
	cargo build --release --all-features

lint:  ## Run Clippy for linting, rustfmt for autoformat checks
	cargo clippy --all-features
	cargo fmt --all -- --check

fix:  ## Fix code with rustfmt
	cargo fmt --all

check:
	cargo check --all-features

tests:  ## Run the tests
	cargo llvm-cov nextest --cobertura --output-path junit.xml

coverage:
	cargo llvm-cov nextest --lcov --output-path coverage

# aliases
develop: dev
test: tests
format: fix
checks: check

# Thanks to Francoise at marmelab.com for this
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

print-%:
	@echo '$*=$($*)'
