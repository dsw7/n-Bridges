.PHONY = help convex dist convex-groupby test

PYTHON_INTERP = /usr/bin/env python3
ROOT_DIRECTORY := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

define HELP_LIST_TARGETS
To display all targets:
    $$ make help
Generate {phe,tyr,trp}_3d_bridges.png convex hull plots:
    $$ make convex
Generate {(phe|tyr|trp)_(phe|tyr|trp)_(phe|tyr|trp)}_3d_bridges.png grouped convex hull plots:
    $$ make convex-groupby
Generate distribution.png:
    $$ make dist
Run unit tests:
    $$ make test
endef

export HELP_LIST_TARGETS

help:
	@echo "$$HELP_LIST_TARGETS"

convex:
	@$(PYTHON_INTERP) $(ROOT_DIRECTORY)/convex_hulls/get_convex_hulls.py

convex-groupby:
	@$(PYTHON_INTERP) $(ROOT_DIRECTORY)/convex_hulls_groupby/get_convex_hulls_groupby.py

dist:
	@$(PYTHON_INTERP) $(ROOT_DIRECTORY)/distributions/get_3_bridge_distribution.py

test:
	@$(PYTHON_INTERP) -m pytest --verbose --capture=no $(ROOT_DIRECTORY)/tests
