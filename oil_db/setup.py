#!/usr/bin/env python
import os
import sys
import fnmatch
import shutil
from pathlib import Path

from setuptools import setup, find_packages
from distutils.command.clean import clean

from setuptools import Command
from setuptools.command.test import test as TestCommand


def get_version(pkg_name):
    """
    Reads the version string from the package __init__ and returns it
    """
    with open(os.path.join(pkg_name, "__init__.py")) as init_file:
        for line in init_file:
            parts = line.strip().partition("=")
            if parts[0].strip() == "__version__":
                return parts[2].strip().strip("'").strip('"')
    return None


pkg_name = 'oil_database'
here = Path(__file__).resolve().parent
# here = os.path.abspath(os.path.dirname(__file__))
README = (here / '../README.md').open().read()
pkg_version = get_version(pkg_name)

db_name = 'oil_database'
connection_alias = 'oil-db-app'  # specific to PyMODM


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


class init_database(Command):
    '''
        Command to construct the oil database.  We basically re-use the
        database initialization script function, but wrap it in a setup
        command.
    '''
    description = 'make the oil database'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from oil_database.scripts.db_initialize import init_db_cmd

        init_db_cmd(('oil_db_init',))


class PyTest(TestCommand):
    '''
    So we can run tests with 'setup.py test'
    '''

    def finalize_options(self):
        TestCommand.finalize_options(self)
        # runs the tests from inside the installed package
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # no idea why it doesn't work to call pytest.main
        # import pytest
        # errno = pytest.main(self.test_args)
        errno = os.system('py.test --pyargs oil_database')
        sys.exit(errno)


setup(name=pkg_name,
      version=pkg_version,
      description=('{}: {}'.format(pkg_name,
                                   'The NOAA library of oils '
                                   'and their properties.')),
      long_description=README,
      long_description_content_type='text/markdown',
      author='ADIOS/GNOME team at NOAA ORR',
      author_email='orr.gnome@noaa.gov',
      classifiers=['Programming Language :: Python',
                   'Framework :: Pyramid',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                   ],
      keywords='adios gnome oilspill weathering trajectory modeling',
      url='',
      packages=find_packages(),
      include_package_data=True,
      package_data={'oil_database': ['OilLib',
                                     'tests/*.py']},
      cmdclass={'init_db': init_database,
                'cleanall': cleanall,
                'test': PyTest,
                },
      entry_points={'console_scripts': [('oil_db_init = '
                                         'oil_database.scripts.db_initialize'
                                         ':init_db_cmd'),
                                        ('oil_db_import = '
                                         'oil_database.scripts.db_import'
                                         ':import_db_cmd'),
                                        ('export_ec = '
                                         'oil_database.scripts.export_to_csv'
                                         ':export_to_csv_cmd'),
                                        ],
                    },
      zip_safe=False,
      )
