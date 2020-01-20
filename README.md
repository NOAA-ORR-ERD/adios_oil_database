# ADIOS Oil Database

## Dev Process:

As of Jan, 2019, we are in a push to get an MVP working to deliver to BSEE. So we are working in the develop branch, and actively pushing changes. When its gets more stable, we will start pushing to master, but for now -- do everything in develop.

i.e.:

If it's not trivial, and might step on others' toes, create a branch for a new feature or fix, when you are happy with it, "rebase" -- i.e. merge the latest develop into your branch. If it's all working, merge it all into develop.

When you push to develop, the CI should run at least some tests, so you'll know if you accidentally broke something -- fix it if you did :-)

# Overview

The ADIOS OIl Database is a "Single page/rich client/AJAX") Web Application with the following components:

The Client is built with the Ember Javascript Framework, which provides a whole pile of javascript, in browser templating, etc. You read more about it on the Web, but for now: it's a bunch of javascript, at run-time, entirely in the Browser.

The Client relies on a JSON REST service, which is provided by a Pyramid App, using Cornice to help with the REST stuff. WE are calling this the "web_api", and the python package is called "oil_database_api".

The web_api uses mongodb to manage the data itself. mongodb (https://www.mongodb.com/) is a "NoSQL Document Database", which runs as a separate server process.

So: to run the app, you need to:

* Serve up the pile of javascript/CSS/static resources etc to the browser to run the client.
* Run the oil_database_api Pyramid App
* Run the mongodb daemon (mongod) to serve the data.

On our staging server, we have these running as three separate services (separate docker containers? not sure, but they could be)

A bit more about Ember:

Ember is a javascript framework -- you use it to write your in-the-browser code. However, it also comes with a set of utilities (ember-cli) that can be used to help manage your code: package it up, manage dependencies, etc. ONe of these is "ember serve" which provides (using node) a way to serve up all the files for development, including reloading when they change, etc.

It also provides "ember build", which builds the app, creating a pile of static files that are needed to run the app -- these static files can be served up by any web server (SimpleHTTPServer seems to work fine, for example) In a production server, we might use Ngnx or Node, or ????

### Electron:

In addition to a server app hosted by NOAA, we want to provide a stand-alone version, so that others (BSEE in particular) can manage their own data, on their own systems, without needing to deploy a server application. Much like CammeoChemical and Tier2Submit.

Electron is a framework for bundling up web apps as a desktop app:

"Electron is an open source library developed by GitHub for building cross-platform desktop applications with HTML, CSS, and JavaScript. Electron accomplishes this by combining Chromium and Node.js into a single runtime "

(https://electronjs.org/)

Much like what we did for CameoChemicals with wxPython and WebKit (and what Micael has done for MarPlot with CEF and his own C++ code, but someone else doing the hard work :-)

For our case, we need not only a Browser, but also the oil_database_api and mongodb servers running to use the app. In CameoChemicals, the host app and the server were written in Python, so we could start up the server in a separate thread, and have it all in one process. I think for Tier2Submit, they are doing a similar thing, but all in C++ (not sure about the threading, but...).

As Electron embeds node, we need to start up the Pyramid app and mongod from javascript, as subprocesses, and hence the need to figure out how to manage them.




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
cd oil_db

python setup.py develop
```

This will install it in "develop" or "editable" mode -- so as you change the source code, the changes will be seen immediately without having to re-install.

#### testing

`pytest --pyargs oil_database`


NOTE: this will skip the database connection tests. If you have mongo running, you can turn them on by running pytest from within the test dir, and passing the --mongo flag:

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
