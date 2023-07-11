help:
	@echo The following makefile targets are available:
	@echo
	@grep -e '^\w\S\+\:' Makefile | sed 's/://g' | cut -d ' ' -f 1
		
requirements:
	pip3 install -U pip
	pip3 install git+https://github.com/ethereum/web3.py.git
	pip3 install -e ./src

clean:
	find . -name '*.pyc' -delete
	rm -rf src/build
	rm -rf src/*.egg-info

test:
	pytest ./src

-include ./src/test-one.mk
test-one:
	pytest -k $(TEST_ONE) ./src
