This dir hosts the documentation of the adios_db python package

It is built with the "Sphinx" documentation system.

Sphinx created documents in various format from source written in Restructured Text (the .rst files you see here)

It also can use "autodoc" to automatically generate the documentation of the code from the docs in the code itself.

These docs are a combination of hand-written docs and a full set auto-generated from the code

For more details and help with Sphinx, see:

https://www.sphinx-doc.org/en/master/

Building the docs
=================

You must have Sphinx installed to build the docs::

  conda install sphinx

Building the html docs
----------------------

At this point, only html docs have been configured. IT's pretty easy::

    make html

Should do it.

The docs get built in the ``build/html`` directory. Point your browser to ``index.html`` to see them.


Autodoc:
--------

NOTE: This only needs to be done if there are changes to the code structure -- changes to the code itself will be included when the docs are built.

If any new files have been added or removed from the code, you need to re-run the ``sphinx-apidoc`` script, with appropriate flags::

  sphinx-apidoc --force --no-toc --module-first -o source/api ../../adios_db ../../adios_db/test/

There is a handy script here that will do that for you:

OS-X or Linux: ``build_api_docs.sh``

Windows: ``build_api_docs.bat``

NOTE: After running this script, you may need to add any new generated files to git. Run ``git status`` to check.


