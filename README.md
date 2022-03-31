# ADIOS Oil Database

ADIOS Oil Database project: system for managing oil properties data for use in Oil Spill Response. It is the code behind the Web Application at:

http://adios.orr.noaa.gov


This repository contains three packages:

``adios_db``: Python Package for managing the data.

``adios_db_api``: A Python / Pyramid web application that provides a JSON-API for accessing the data.

``ADIOS web_client``: Ember-JS based Web browser client for searching, viewing, and modifying the data.

## Oil Data

This package includes a small set of data in JSON format used for testing. The full dataset managed by NOAA can be found in the noaa-oil-data project here:

https://github.com/NOAA-ORR-ERD/noaa-oil-data


## Dev Process:

As of March, 2022, the project is still under active development, though nearly at a stable state.

It is developed in an internal NOAA git repository. We try to keep the gitHub version up to date, but it may be a bit behind.
If you find issues in or have questions about the code, reach out to NOAA (gitHub issues are good for questions) and we will work to push the latest version and address your questions.

The "production" branch is the stable branch, and is the code behind the live web application.

We are doing active development in the develop branch, which we try to keep up to date as well.


## Web Application Overview

The ADIOS Oil Database is a "Single page/rich client/AJAX" Web Application with the following components:

The Client is built with the Ember Javascript Framework, which provides a whole pile of javascript, in browser templating, etc. You can read more about it on the Web, but in short: it's a bunch of javascript, at run-time, entirely in the Browser.

The Client relies on a JSON REST service, which is provided by a Python/Pyramid Application, using Cornice to help with the REST stuff. This is the "web_api", and the python package is called "adios_db_api".

The adios_db_api uses mongodb to manage the data itself. mongodb (https://www.mongodb.com/) is a "NoSQL Document Database", which runs as a separate server process.

So: to run the app, you need to:

* Serve up the pile of javascript/CSS/static resources etc to the browser to run the client.
* Run the adios_db_api Pyramid App
* Run the mongodb daemon (mongod) to serve the data.

On NOAA's production server, these are running as three separate services (separate docker containers)

### A bit more about Ember:

Ember is a javascript framework -- you use it to write your in-the-browser code. However, it also comes with a set of utilities (ember-cli) that can be used to help manage your code: package it up, manage dependencies, etc. One of these is "ember serve" which provides (using node) a way to serve up all the files for development, including reloading when they change, etc.

It also provides "ember build", which builds the app, creating a pile of static files that are needed to run the app -- these static files can be served up by any web server (Ngnx, Apache, etc.)

### Electron:

In addition to a server app hosted by NOAA, we have developed a prototype of a stand-alone version, so that others can manage their own data, on their own systems, without needing to deploy a server application.

Electron is a framework for bundling up web apps as a desktop app:

"Electron is an open source library developed by GitHub for building cross-platform desktop applications with HTML, CSS, and JavaScript. Electron accomplishes this by combining Chromium and Node.js into a single runtime "

(https://electronjs.org/)

There is prototype code that worked for providing a desktop app, but it has not been tested recently. Please contact us if you are interested in this functionality.

## Components

### `adios_db`:

Python package for managing the data. It provides code for:

 * Importing data
 * Reading and writing the JSON format
 * A data validation framework (there is a small amount of validation included, it is fairly starightformward to add more.
 * Serving the data via MongoDB
 * Extracting specific data.
 * Managing physical units, including unit conversion.
 * Some computation on the data (interpolation, etc.)
 * Code to build an oil definition as required by the NOAA GNOME model.

Docs at: https://noaa-orr-erd.github.io/adios_oil_database/

<<<<<<< HEAD
Python package for managing the data. It provides code for:

 * Importing data
 * Reading and writing the JSON format
 * A data validation framework (there is a small amount of validation included, it is fairly starightformward to add more.
 * Serving the data via MongoDB
 * Extracting specific data.
 * Managing physical units, including unit conversion.
 * Some computation on the data (interpolation, etc.)
 * Code to build an oil definition as required by the NOAA GNOME model.
=======
>>>>>>> production

### `adios_db_api`:

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


## Installing the ``adios_db`` package:


#### Setup and activate a conda environment:

```
conda create -n adios_db --file adios_db/conda_requirements.txt
conda activate adios_db
```

#### Install the package

```
$ cd adios_db
```

For development (editable mode):

```
$ pip install -e .
```

For use (regular install):

```
$ pip install .
```

#### Testing the adios_db package

While developing -- run pytest in the test dir:

```
$ cd adios_db/test

$ pytest
```

If you want to test the MongoDB serving capability, you need to have mongod running, and then pass the --mongo flag to pytest:

```
$ mongod -f mongo_config_dev.yaml
$ pytest --mongo
```

Testing the installed version, run pytest from anywhere:

```
$ pytest --pyargs adios_db
```

## Installing the Web API

### If you have not already created a conda environment:

```
conda create -n adiosdb --file oil_db/conda_requirements.txt --file web_api/conda_requirements.txt
```

This will `create` a new environment with the name (`-n`) adiosdb, using the requirements `--file`s in the oil_db and web_api directories.

To use this new environment, you need to activate it:

```
conda activate adiosdb
```

### If you have already created a conda environment:

Activate your adios_db environment, if it's not already activated:

```
conda activate adiosdb
```

Install the dependencies (it's good to pass the adios_db ones in, even if they have already been installed, so conda won't get confused)

```
conda install --file oil_db/conda_requirements.txt --file web_api/conda_requirements.txt
```

## MongoDB

The oil_db code needs a mongodb instance running to support the web_api. It can be used without mongo for most scripting activities.

MongoDB can be installed in various ways, and which is best depends on platform and deployment environment. But the easiest way on Windows and Mac for development is to use conda to install it:

```
conda install mongodb
```

## Installing the the Web Client

The webclient needs node, which can be installed in various way, but can also be gotten from conda:

```
$ conda install nodejs
```

### Installing the web_api package:

```
$ cd ../web_api

$ pip install -e .
```

### Starting mongodb:

Mongodb needs to be running for all of the tests to work:

`mongod -f mongo_config_dev.yml`

will start the mongo daemon with the given config -- set up for development. You may want to do that it its own terminal.

### Testing

By default, testing will skip the database connection tests. If you have mongo running, you can turn them on by running pytest from within the test dir, and passing the --mongo flag:

```
cd adios_db/test

pytest --mongo
```

### Initializing the database:

NOTE: This is a bit out of date -- it should work, but in general, you don't wnat to re-import all the data every time, but rather, work with a pre-build database, which can be loaded from JSON files.

Create an empty DB

```
oil_db_init
```
Import the data we have so far (only if you want )

```
oil_db_import --all
```

### testing

pytest --pyargs oil_database_api


## Running the app:

### Starting the API:

`pserve --reload config-example.ini`

### Running the client:

See the README in the web_client dir.


## Running the Full App locally

There is an experimental script: ``run_app.py`` that you can use to run the full stack with one command. It has not been well tested or maintained.

It must be run within the conda environment you want to use for this app. If you aren't doing anything else with conda, that could be the base environment, but we recommend you use one for this app.

* Setup and activate a conda environment:

```
conda create -n adios_db --file adios_db/conda_requirements.txt
conda activate adios_db
```
* Setup everything:

```
python run_app.py --setup
```

The ``--rebuild`` (``-r``) flag will update the dependencies and rebuild the client app.

The ``--database`` (``-d``) flag will rebuild the database

The ``--setup`` flag will install / update all the dependencies, and rebuild the database, but not start the server.


* Running the app:

```
python run_app.py
```

With no flags, should run the app itself, with the existing code and data.

## Project team:

Program Manager: Chris Barker

Project Manager and lead chemist: Robert Jones

Chemist: Dalina Thrift-Viveros

Software Developers: James Makela, Gennady Kachook

Data Manager: Jeff Lankford
