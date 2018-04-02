.SUFFIXES:
.PHONY: all build

CC	:= gcc
CFLAGS	:= -g -Wall -Wstrict-prototypes

export CC
export CFLAGS

PYTHON := python3.5

test: build
	$(PYTHON) unittests.py

build:
	echo $$CFLAGS
	$(PYTHON) setup.py build_ext --inplace

clean:
	rm -f *.so

sdist bdist:
	$(PYTHON) setup.py $@


# ----------------------------------------------------------------------

VERSION := 1.2.0

VENV_PATH ?= /opt/venv
REPO_NAME ?= artifactory

install: sdist
	$(VENV_PATH)/pip install --upgrade dist/pyDAWG-$(VERSION).tar.gz

upload: sdist
	$(VENV_PATH)/bin/python setup.py sdist upload -r $(REPO_NAME)
