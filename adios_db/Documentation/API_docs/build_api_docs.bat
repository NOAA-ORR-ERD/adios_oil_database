rem build API docs

rem This script runs the sphinx-apidoc command with a few flags.

rem This is a Windows batch file version -- untested!
rem   if it works, please remove this comment :-)

sphinx-apidoc --force --no-toc --module-first -o source/api ../../adios_db ../../adios_db/test/


