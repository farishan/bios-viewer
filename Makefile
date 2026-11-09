.PHONY: run test lint smoke install clean

PYTHON ?= python3

run:
	PYTHONPATH=src $(PYTHON) -m bios_viewer

test:
	PYTHONPATH=src $(PYTHON) -m pytest

lint:
	$(PYTHON) -m compileall -q src tests

smoke: lint
	PYTHONPATH=src $(PYTHON) -c "import bios_viewer; print('import ok', bios_viewer.__version__)"

install:
	$(PYTHON) -m pip install --user .

clean:
	rm -rf build dist *.egg-info .pytest_cache __pycache__ src/*/__pycache__ tests/__pycache__