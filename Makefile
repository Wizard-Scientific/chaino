help:
	@echo The following makefile targets are available:
	@echo
	@grep -e '^\w\S\+\:' Makefile | sed 's/://g' | cut -d ' ' -f 1
		
requirements:
	pip3 install -U pip
	pip3 install -e .

clean:
	find . -name '*.pyc' -delete
	rm -rf build
	rm -rf *.egg-info

test:
	pytest -p no:warnings .

-include ./tests/one.mk
test-one:
	pytest -p no:warnings -k $(TEST_ONE) .

###
# Examples

var:
	mkdir -p var

fantom-blocks: var
	python3 ./scripts/blockchain.py download fantom 1 1000 var/fantom

fantom-transactions: var
	python3 ./scripts/blockchain.py transactions-csv 1 1000 var/fantom | gzip > var/fantom-txs.csv.gz

bsc-blocks: var
	python3 ./scripts/blockchain.py download bsc 1 1000 var/bsc

bsc-transactions: var
	python3 ./scripts/blockchain.py transactions-csv 1 1000 var/bsc | gzip > var/bsc-txs.csv.gz
