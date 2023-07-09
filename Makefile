help:
	@echo The following makefile targets are available:
	@echo
	@grep -e '^\w\S\+\:' Makefile | sed 's/://g' | cut -d ' ' -f 1
		
requirements:
	pip install -U pip
	pip install -e ./src

clean:
	find . -name '*.pyc' -delete
	rm -rf src/build
	rm -rf src/*.egg-info
