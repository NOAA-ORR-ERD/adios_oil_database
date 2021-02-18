#!/bin/sh

# build API docs
# This script runs the sphinx-apidoc command with a few flags.

sphinx-apidoc --force --no-toc --module-first -o source/api ../../adios_db ../../adios_db/test/

# rm source/api/modules.rst

