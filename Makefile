help:
	@echo The following makefile targets are available:
	@echo
	@grep -e '^\w\S\+\:' Makefile | sed 's/://g' | cut -d ' ' -f 1
		
requirements:
	pip3 install -U pip
	pip3 install -e .

clean:
	find . -name '*.pyc' -delete
	rm -rf src/build
	rm -rf src/*.egg-info

test:
	pytest -p no:warnings ./src

-include ./src/test-one.mk
test-one:
	pytest -p no:warnings -k $(TEST_ONE) ./src
