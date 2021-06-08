.PHONY = help convex dist

PYTHON_INTERP = /usr/bin/python3
ROOT_DIRECTORY := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

define HELP_LIST_TARGETS
To display all targets:
    $$ make help
Generate {phe,tyr,trp}_3d_bridges.png convex hull plots:
    $$ make convex
Generate distribution.png:
    $$ make dist
endef

export HELP_LIST_TARGETS

help:
	@echo "$$HELP_LIST_TARGETS"

convex:
	@$(PYTHON_INTERP) $(ROOT_DIRECTORY)/convex_hulls/get_convex_hulls.py

dist:
	@$(PYTHON_INTERP) $(ROOT_DIRECTORY)/distributions/get_3_bridge_distribution.py
