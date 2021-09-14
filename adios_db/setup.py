#!/usr/bin/env python
import os
import fnmatch
import shutil
from pathlib import Path

from setuptools import setup, find_packages
from distutils.command.clean import clean


def get_version(pkg_name):
    """
    Reads the version string from the package __init__ and returns it
    """
    with open(Path(pkg_name) / "__init__.py",
              encoding="utf-8") as init_file:
        for line in init_file:
            parts = line.strip().partition("=")
            if parts[0].strip() == "__version__":
                return parts[2].strip().strip("'").strip('"')
    return None


pkg_name = 'adios_db'
here = Path(__file__).resolve().parent
README = (here / 'README.md').open().read()
pkg_version = get_version(pkg_name)

pkg_data = ["models/oil/product_types_and_labels.csv",
            "test/test_models/test_oil/example_products.csv",
            "test/data_for_testing/example_data/**/*.json",
            "test/data_for_testing/noaa-oil-data/oil/**/*.json",
            # so the output dir will be there.
            "/test/test_models/test_oil/output/empty_file",
            ]


def clean_files():
    #  Fixme: doesn't this get cleaned up by the standard "clean"?
    src = here / pkg_name

    to_rm = []
    for root, _dirnames, filenames in os.walk(src):
        for filename in fnmatch.filter(filenames, '*.pyc'):
            to_rm.append(os.path.join(root, filename))

    to_rm.extend([os.path.join(here, '{0}.egg-info'.format(pkg_name)),
                  os.path.join(here, 'build'),
                  os.path.join(here, 'dist')])

    for f in to_rm:
        print('Deleting {0} ..'.format(f))
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except Exception:
            pass

class cleanall(clean):
    description = 'cleans files generated by "develop"'

    def run(self):
        # clean is an old-style class, so we can't use super()
        clean.run(self)
        clean_files()

# this really shouldn't be happening at package install anyway
# class init_database(Command):
#     '''
#         Command to construct the oil database.  We basically re-use the
#         database initialization script function, but wrap it in a setup
#         command.
#     '''
#     description = 'make the oil database'
#     user_options = []

#     def initialize_options(self):
#         pass

#     def finalize_options(self):
#         pass

#     def run(self):
#         from adios_db.scripts.db_initialize import init_db_cmd

#         init_db_cmd(('adios_db_init',))

# # this really isn't needed these days:
# class PyTest(TestCommand):
#     '''
#     So we can run tests with 'setup.py test'
#     '''

#     def finalize_options(self):
#         TestCommand.finalize_options(self)
#         # runs the tests from inside the installed package
#         self.test_args = []
#         self.test_suite = True

#     def run_tests(self):
#         # no idea why it doesn't work to call pytest.main
#         # import pytest
#         # errno = pytest.main(self.test_args)
#         errno = os.system('py.test --pyargs adios_db')
#         sys.exit(errno)

scripts = ['adios_db_init = adios_db.scripts.db_initialize:init_db_cmd',
           'adios_db_import = adios_db.scripts.db_import:import_db_cmd',
           'adios_db_oil_query = adios_db.scripts.oil_query:oil_query_cmd',
           'adios_db_backup = adios_db.scripts.db_backup:backup_db_cmd',
           'adios_db_restore = adios_db.scripts.db_restore:restore_db_cmd',
           'adios_db_validate = adios_db.scripts.validate:main',
           'adios_db_update_test_data = adios_db.scripts.update_test_data:main',
           'adios_db_process_json = adios_db.scripts.process_json:run_through',
           ]

print("package data is:", pkg_data)

setup(name=pkg_name,
      version=pkg_version,
      description=('{}: {}'.format(pkg_name,
                                   'Python library for working with the'
                                   'NOAA ADIOS Oil Database')),
      long_description=README,
      long_description_content_type='text/markdown',
      author='ADIOS/GNOME team at NOAA ORR',
      author_email='orr.gnome@noaa.gov',
      classifiers=['Programming Language :: Python',
                   'Programming Language :: Python :: 3 :: Only',
                   'Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Chemistry',
                   ],
      keywords='adios gnome oilspill weathering trajectory modeling',
      url='',
      packages=find_packages(),
      # include_package_data=True,
      package_data={'adios_db': pkg_data},
      entry_points={'console_scripts': scripts},
      zip_safe=False,
      )
