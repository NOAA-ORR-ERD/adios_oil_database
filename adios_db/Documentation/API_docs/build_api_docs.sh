#!/bin/sh

# build API docs
# This script runs the sphinx-apidoc command with a few flags.

sphinx-apidoc --force --no-toc -o source/api ../../adios_db
