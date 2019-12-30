# ADIOS Oil Database

Lot of code

## Components

### `oil_db`:

Python package for managing the data -- using a MongoDB back end.

### `web_api`:

Python (Pyramid) web server for interaction between the database and the Web client.

### `web_client`:

Single page web app (emberjs based)for displaying and editing the data.


## Installing for development:

### conda setup:

We are using conda wherever possible for getting all the dependencies.

To get conda going:

* Install miniconda: https://docs.conda.io/en/latest/miniconda.html
  (Python 3 version is best at this point)

* We use a lot of packages from the "conda-forge" channel, so you
  need to add that to your conda config:

```
conda config --add channels conda-forge
```

* If you are only working on one project, you can use the "base"
  environment, but it is usually best to create an environment for
  each specific project -- each environment can have a different set of dependencies, including Python itself.

```
conda create -n adiosdb --file oil_db/conda_requirements.txt --file web_api/conda_requirements.txt
```

This will `create` a new environment with the name (`-n`) adiosdb, using the requirements `--file`s in the oil_db and web_api directories.

To use this new environment, you need to activate it:

```
conda activate adiosdb
```

There are a couple packages that are not (yet) available in conda-forge, so those need to be installed with pip:

```
pip install --no-deps -r oil_db/pip_requirements.txt

pip install --no-deps -r web_api/pip_requirements.txt
```

(It's a good idea to use --no-deps, so that pip won't update stuff that conda already installed)

## MongoDB

The oil_db code needs a mongodb instance running. It can be installed in various ways, and which is best depends on platform and deployment environment. But the easiest way on Windows and Mac for development is to use conda to install it:

```
conda install mongodb
```

The webclient needs node, which can be installed in various way, but can also be gotten from conda:

```
conda install nodejs
```

### Installing the oil_database package:

```
cd oil_database

python setup.py develop
```

This will install it in "develop" or "editable" mode -- so as you change the source code, the changes will be seen immediately without having to re-install.

It's a good idea to run the tests:

pytest --pyargs oil_database

If they all pass, you're good to go.


### Installing the web_api package:

```
cd ../web_api

python setup.py develop
```







## Project team:

Program Manager (and primary contact with BSEE): Chris Barker

Project Manager and lead chemist: Robert Jones

Chemist: Dalina Thrift-Vivaros

Software Developers: James Makela, Gennady Kachook

