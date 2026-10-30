PYTHON ?= python3
CONFIG ?= config.yaml

.PHONY: run test check

run:
	$(PYTHON) main.py --config "$(CONFIG)"

test:
	$(PYTHON) -m unittest discover -s tests -v

check: test
