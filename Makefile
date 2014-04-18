HOME ?= $HOME
CWD = $(shell pwd)
VENVS ?= $(HOME)/.virtualenvs
PYTHON2 = $(VENVS)/builder2.7/bin/python2.7
PYTHON3 = $(VENVS)/builder3.4/bin/python3.4
PYTHONS = $(VENVS)/builder2.6/bin/python2.6 $(VENVS)/builder2.7/bin/python2.7 $(VENVS)/builder3.2/bin/python3.2 $(VENVS)/builder3.3/bin/python3.3 $(VENVS)/builder3.4/bin/python3.4

.PHONY: all test clean help register build

all: clean test build register help upload develop environment

environment:
	echo "HOME $(HOME)"
	echo "VENVS $(VENVS)"
	echo "PYTHONS $(PYTHONS)"

clean:
	$(PYTHON2) setup.py clean;
	rm -rf *.egg-info;
	rm -rf *.egg;
	rm -rf build;
	rm -rf dist;

test:
	for python in $(PYTHONS); do\
		PYTHONPATH=$(CWD) "$$python" setup.py test; \
	done


build:
	$(PYTHON2) setup.py sdist;
	for python in $(PYTHONS); do\
		"$$python" setup.py bdist_egg; \
	done
	$(PYTHON2) setup.py bdist_wheel;
	$(PYTHON3) setup.py bdist_wheel;

register:
	$(PYTHON2) setup.py register;

install:
	sudo $(PYTHON2) setup.py build install;

upload: clean test register build
	$(PYTHON2) setup.py sdist upload --sign;
	for python in $(PYTHONS); do\
		"$$python" setup.py bdist_egg  upload --sign; \
	done
	$(PYTHON2) setup.py bdist_wheel upload --sign;
	$(PYTHON3) setup.py bdist_wheel upload --sign;

help:
	@echo "Reusables"
	@echo ""
	@echo "all          run clean, test and build"
	@echo "build        generate source and egg files"
	@echo "test         test files using nosetests"
	@echo "register     register the new version wiht PyPI"
	@echo "upload       upload results of build to PyPI, will be signed"
	@echo "help         see this message again"

develop:
	sudo add-apt-repository ppa:fkrull/deadsnakes;
	sudo apt-get update;
	sudo apt-get install python2.6 python2.7 python3.2 python3.3 python3.4 pypy;

