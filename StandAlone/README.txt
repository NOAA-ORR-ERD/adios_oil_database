This dir is used to build the stand-alone

There are assorted scripts and configuration files, and it will be built here.

# How to build

We have potentially two ways to build a stand alone:

* recreate a minimal conda environment to be installed as part of the app

* use PyInstaller to build an "executable" which bundles up all the Python stuff

If using PyInstaller, we can use the full conda environment we use for development.

If using a "custom" environment, you can still use the full one to build, but you'll need to create a custom minimal one to package it up.

## minimal conda environment

Do this if you are *not* using PyInstaller

This is a pretty easy step: you simply build an environment in the usual way:

`conda create -n standalone --file standalone_standalone_conda_requirements.txt`

That should create an directory called "standalone" in your miniconda3/envs dir (Or somewhere like that)

In that environment, you should be able to run the full application, but not the tests, and maybe not the data importing scripts. And not any node stuff to run ember and build the app.

To use that environment, you do:

`conda activate standalone`

once activated, you will need to install our packages:

oil_database and oil_database_api are both python packages -- they should be installed into the python in the environment we're delivering with the standalone.

The way to do that is:

```
conda activate standalone
cd oil_db
pip install .
cd ../web_api
pip install .
```

You should be able to build the ember app, and all that, with the full develop environment, and then deactivate that, and activate the standalone environment to test.

(hmm, if you want to run ember without building its app, you may need to install node in the standalone environment first)

## Building the App.

To get the full app running you need:

The oil_database and oil_database_api packages installed in the standalone conda environment.

The ember app built and put somewhere.

Then it should be runnable.

There is a script: `build_standalone.py` in the Standalone directory that should do all that for you. you can look at it to see what it does.

Be default, it updates and builds everything, but you can turn some of that off if you are running it multiple times:

python build_standalone.py --help

You do need to make sure that the standalone environment has our packages installed -- see above.





