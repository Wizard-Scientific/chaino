help:
	@echo The following makefile targets are available:
	@echo
	@grep -e '^\w\S\+\:' Makefile | sed 's/://g' | cut -d ' ' -f 1
		
requirements:
	pip3 install -U pip
	pip3 install -e .[dev]
	pip3 install -e ../nested-filestore

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

-include ./settings.mk
ethereum-transactions: var
	./bin/blockchain.py extract-txs $(BLOCKCHAIN_PATH)/ethereum/blocks $(BLOCKCHAIN_PATH)/ethereum/txs 2,2,2
	./bin/blockchain.py transactions-csv $(BLOCKCHAIN_PATH)/ethereum/txs 2,2,2 ./var/ethereum-txs.csv.gz

arbitrum-transactions: var
	./bin/blockchain.py extract-txs $(BLOCKCHAIN_PATH)/arbitrum/blocks $(BLOCKCHAIN_PATH)/arbitrum/txs 3,3
	./bin/blockchain.py transactions-csv $(BLOCKCHAIN_PATH)/arbitrum/txs 3,3 ./var/arbitrum-txs.csv.gz

.PHONY: docs
