# Oil Database Backend

This is a Python package for managing the database functionality

We are basing the database on MongoDB, an popular object database.

&nbsp;

A couple of command-line applications are delivered along with this package.

---

##### oil\_db\_init

This is a command-line application that initializes the database.

```
$ oil_db_init --help  
usage: oil_db_init [-h] [--config CONFIG]

Database Initialization Arguments:

optional arguments:
  -h, --help       show this help message and exit
  --config CONFIG  Specify a *.ini file to supply application settings. If not
                   specified, the default is to use a local MongoDB server.
```

##### oil\_db\_import

This is a command-line application that imports a number of oil record
data sets into the database.

```
$ oil_db_import --help
usage: oil_db_import [-h] [--all] [--config CONFIG]

Database Import Arguments:

optional arguments:
  -h, --help       show this help message and exit
  --all            Import all datasets, bypassing the menus, and quit the
                   application when finished.
  --config CONFIG  Specify a *.ini file to supply application settings. If not
                   specified, the default is to use a local MongoDB server.
```

&nbsp;

## Quick Development [Re]Installation

```
python setup.py cleanall
python setup.py develop --uninstall
python setup.py develop
yes | oil_db_init
oil_db_import --all
```
