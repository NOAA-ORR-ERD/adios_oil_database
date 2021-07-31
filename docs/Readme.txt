Documentation for the database -- mostly the Web Version.

These are built with the Sphinx documentation system.

The source of the docs is in the ``source`` directory.

To build the docs, you must have Sphinx and the "Read The Docs" theme installed:

conda install --file conda_requirements.txt

then they should build with:

make html

The results will be in the ``build`` directory.