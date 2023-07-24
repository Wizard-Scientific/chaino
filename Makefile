help:
	@echo The following makefile targets are available:
	@echo
	@grep -e '^\w\S\+\:' Makefile | sed 's/://g' | cut -d ' ' -f 1
		
requirements:
	pip3 install -U pip
	pip3 install -e .[dev]
	pip3 install -e ../nested_filestore

clean:
	find . -name '*.pyc' -delete
	rm -rf build
	rm -rf *.egg-info

test:
	pytest -p no:warnings .
	pylint --disable C0114,R0913 ./chaino

-include ./tests/one.mk
test-one:
	pytest -p no:warnings -k $(TEST_ONE) .

docs: var
	rm -rf var/sphinx
	sphinx-build -b html docs var/sphinx

###
# Docker

run-docker:
	docker run \
		--rm -it \
		--name chaino \
		-v /tmp/chaino:/mnt/chaino \
		chaino:local

build-docker:
	docker build -t chaino:local .

build-docker-rebuild:
	docker build --no-cache -t chaino:local .

###
# Examples

var:
	mkdir -p var

fantom-blocks: var
	./bin/blockchain.py download fantom 1 1000 var/fantom

fantom-transactions: var
	./bin/blockchain.py transactions-csv 1 1000 var/fantom | gzip > var/fantom-txs.csv.gz

bsc-blocks: var
	./bin/blockchain.py download bsc 1 1000 var/bsc

bsc-transactions: var
	./bin/blockchain.py transactions-csv 1 1000 var/bsc | gzip > var/bsc-txs.csv.gz

.PHONY: docs
