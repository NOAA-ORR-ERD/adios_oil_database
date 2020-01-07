# ADIOS Oil Database

## Dev Process:

As of Jan, 2019, we are in a push to get an MVP working to deliver to BSEE. So we are working in the develop branch, and actively pushing changes. When its gets more stable, we will start pushing to master, but for now -- do everything in develop.

i.e.:

If it's not trivial, and might step on others' toes, create a branch for a new feature or fix, when you are happy with it, "rebase" -- i.e. merge the latest develop into your branch. If it's all working, merge it all into develop.

When you push to develop, the CI should run at least some tests, so you'll know if you accidentally broke something -- fix it if you did :-)


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

#### testing

`pytest --pyargs oil_database`


NOTE: this will skip teh database connection tests. If you have mongo running, you can turn them on by running pytest from within the test dir, and passing the --mongo flag:

```
cd oil_database/test

pytest --mongo
```

### Installing the web_api package:

```
cd ../web_api

python setup.py develop
```

### Starting mongodb:

Mongodb needs to be running for all of the tests to work:

`mongod -f mongo_config_dev.yml`

will start the mongo daemon with the given config -- set up for development. You may want to do that it its own terminal.

### Initializing the database:

Create an empty DB

```
oil_db_init
```
Import the data we have so far:

```
oil_db_import --all
```

### testing

pytest --pyargs oil_database_api


## Running the app:

To run the app, you need to be running the database (`mongod`), the API server, and the client code. There is a single script that will do that all for you:

```
run_app.py
```
(Make sure you are in a fully configured environment first -- i.e. `conda activate adiosdb`)

Note that `ember serve` takes a while to get started, so it won't work right away.

hit `^C` to stop everything.

If you want to know how to run each piece, read the script, and/or read on ...

## Starting the API:

`pserve --reload config-example.ini`

## Running the client:

See the README in the web_client dir.


## Project team:

Program Manager (and primary contact with BSEE): Chris Barker

Project Manager and lead chemist: Robert Jones

Chemist: Dalina Thrift-Viveros

Software Developers: James Makela, Gennady Kachook
