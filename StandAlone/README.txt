This dir is used to build the stand-alone

There are assorted scripts and configuration files, and it will be built here.

# How to build

We have potentially two ways to build a stand alone:

* recreate a minimal conda environment to be installed as part of the app

* use PyInstaller to build an "executable" which bundles up all the Python stuff

If using PyInstaller, we can use the full conda environment we use for development.

If using a "custom" environment, you can still use the full one to build, but you'll need to create a custom minimal wine to package it up.

## minimal conda environment

Do this if you are *not* using PyInstaller

This is a pretty easy step: you simply build an environment in the usual way:

`conda create -n standalone standalone_standalone_conda_requirements.txt`

That should create an directory called "standalone" in your miniconda3/envs dir (Or somewhere like that)

In that environment, you should be able to run the full application, but not the tests, and maybe not the data importing scripts. And not any node stuff to run ember and build the app.

To use that environment, you do:

`conda activate standalone`

You should be able to build the ember app, and all that, with the full develop environment, and then deactivate that, and activate the standalone environment to test.

(hmm, if you want to run ember without building its app, you may need to install node in the standalone environment first)

## Building the App.

To get the full app running you need:

The oil_database and oil_database_api packages installed in the standalone conda environment.

The ember app built and put somewhere.

Then it should be runnable.

There is a script: `build_standalone.py` in the Standalone directory that should do all that.


