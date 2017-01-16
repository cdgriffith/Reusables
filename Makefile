HOME ?= $HOME
CWD = $(shell pwd)
VENVS ?= $(HOME)/.virtualenvs
PYTHON2 = $(VENVS)/builder2.7/bin/python2.7
PYTHON2BIN = $(VENVS)/builder2.7/bin
PYTHON3BIN = $(VENVS)/builder3.6/bin
PYTHON3 = $(VENVS)/builder3.5/bin/python3.6
PYTHONS = $(VENVS)/builder2.6/bin/python2.6 $(VENVS)/builder2.7/bin/python2.7 $(VENVS)/builder3.5/bin/python3.5 $(VENVS)/builder3.3/bin/python3.3 $(VENVS)/builder3.4/bin/python3.4 $(VENVS)/builder3.6/bin/python3.6
PYPY = $(VENVS)/builderpypy/bin/python

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
	rm -rf cover;
	rm -rf build;
	rm -rf dist;

test:
	$(PYTHON3BIN)/tox;
#	(set -e; for python in $(PYTHONS); do\
#		PYTHONPATH=$(CWD) "$$python" setup.py test; \
#	done)


build:
	$(PYTHON2) setup.py sdist;
	$(PYTHON2) setup.py bdist_wheel;
	$(PYTHON3) setup.py bdist_wheel;
# for python in $(PYTHONS); do\
 	"$$python" setup.py bdist_egg; \
 done

rstcheck:
	$(PYTHON2BIN)/rstcheck README.rst;


register:
	$(PYTHON2) setup.py register;

install:
	sudo $(PYTHON2) setup.py build install;

upload: clean test register build
	$(PYTHON2) setup.py sdist upload;
	$(PYTHON2) setup.py bdist_wheel upload;
	$(PYTHON3) setup.py bdist_wheel upload;

# for python in $(PYTHONS); do\
	 "$$python" setup.py bdist_egg  upload; \
 done

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
	sudo apt-get install python2.6 python2.6-dev python2.7 python2.7-dev python3.3 python3.3-dev python3.4 python3.4-dev python3.5 python3.5-dev python3.6 python3.6-dev pypy pypy-dev python-pip unrar -y;
	sudo pip install virtualenv --upgrade;
	rm -rf $(VENVS);
	mkdir -p $(VENVS);
	virtualenv -p python2.6 $(VENVS)/builder2.6;
	virtualenv -p python2.7 $(VENVS)/builder2.7;
	virtualenv -p python3.3 $(VENVS)/builder3.3;
	virtualenv -p python3.4 $(VENVS)/builder3.4;
	virtualenv -p python3.5 $(VENVS)/builder3.5;
	virtualenv -p python3.6 $(VENVS)/builder3.6;
	virtualenv -p pypy $(VENVS)/builderpypy;
	$(PYTHON2BIN)/pip install rstcheck --upgrade;
	$(PYTHON3BIN)/pip install tox;