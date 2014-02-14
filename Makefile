.PHONY: all test clean help register build

all: clean test build

clean:
	python setup.py clean;
	rm -rf *.egg-info;
	rm -rf *.egg;
	rm -rf build;
	rm -rf dist;

test:
	python2.6 setup.py test;
	python2.7 setup.py test;
	python3.2 setup.py test;
	python3.3 setup.py test;
	pypy setup.py test;

build:
	python setup.py sdist;
	python2.6 setup.py bdist_egg;
	python2.7 setup.py bdist_egg;
	python3.2 setup.py bdist_egg;
	python3.3 setup.py bdist_egg;
	pypy setup.py bdist_egg;

register:
	python2.7 setup.py register;

install:
	sudo python setup.py build install;

upload: clean test register
	python setup.py sdist upload --sign;
	python2.6 setup.py bdist_egg upload --sign;
	python2.7 setup.py bdist_egg upload --sign;
	python3.2 setup.py bdist_egg upload --sign;
	python3.3 setup.py bdist_egg upload --sign;

help:
	echo "Reusables"
	echo ""
	echo "all: run clean, test and build"
	echo "build: generate source and egg files for python 2.6, 2.7, 3.2, 3.3 and pypy"
	echo "test: test using setup.py test against 2.6, 2.7, 3.2, 3.3 and pypy"
	echo "register: register the new version wiht PyPI"
	echo "upload: upload results of build to PyPI, will be signed"
	echo "help: see this message again"

develop:
	sudo add-apt-repository ppa:fkrull/deadsnakes;
	sudo apt-get update;
	sudo apt-get install python2.6 python2.7 python3.2 python3.3 pypy;