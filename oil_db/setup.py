#!/usr/bin/env python
import os
import sys
import fnmatch
import shutil
import logging

from setuptools import setup, find_packages
from distutils.command.clean import clean

from setuptools import Command
from setuptools.command.test import test as TestCommand

from pymongo.errors import ConnectionFailure


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, '../README.md')).read()
pkg_name = 'oil_database'
pkg_version = '0.0.1'

db_name = 'oil_database'
connection_alias = 'oil-db-app'  # specific to PyMODM

def clean_files():
    src = os.path.join(here, r'oil_database')

    to_rm = []
    for root, _dirnames, filenames in os.walk(src):
        for filename in fnmatch.filter(filenames, '*.pyc'):
            to_rm.append(os.path.join(root, filename))

    to_rm.extend([os.path.join(here, '{0}.egg-info'.format(pkg_name)),
                  os.path.join(here, 'build'),
                  os.path.join(here, 'dist')])

    for f in to_rm:
        print "Deleting {0} ..".format(f)
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except Exception:
            pass


class cleanall(clean):
    description = "cleans files generated by 'develop' and SQL lite DB file"

    def run(self):
        clean.run(self)
        clean_files()


class make_db(Command):
    '''
        Custom command to construct the oil database.  This will be slightly
        different than the previous version of this project.
        - The database is seen as a more permanent entity.  Rebuilding the
          database from source records is potentially destructive of any
          updates that may have happened during the lifetime of the database.
        - If the database collections exist, we will confirm that this action
          is to be taken with a prompt of some kind.
        - If confirmed, we will:
          - initialize the collections in the database.
          - load the database from our data sources.  These will include only
            the OilLib flat file for now, but I imagine other sources to be
            added eventually.
    '''
    description = "make the oil database"
    user_options = user_options = []

    def initialize_options(self):
        '''
            TODO: We will maybe want to specify where our database is in a
                  config instead of just using the defaults.
        '''
        fm_files = '\n'.join([os.path.join(here, 'data', fn)
                              for fn in ('OilLib.txt',)])
        ec_files = '\n'.join([os.path.join(here, 'data', 'env_canada', fn)
                              for fn in ('Physiochemical properties of '
                                         'petroleum products-EN.xlsx',)])
        exxon_files = '\n'.join(self._get_exxon_files())

        blacklist_file = os.path.join(here, 'data', 'blacklist_whitelist.txt')

        self.settings = {'oildb.fm_files': fm_files,
                         'oildb.ec_files': ec_files,
                         'oildb.exxon_files': exxon_files,
                         'blacklist.file': blacklist_file,
                         'mongodb.host': 'localhost',
                         'mongodb.port': 27017,
                         'mongodb.database': db_name,
                         'mongodb.alias': connection_alias}

        try:
            from oil_database.util.db_connection import connect_mongodb

            self.client = connect_mongodb(self.settings)
            print 'Connected successfully!!!'
        except ConnectionFailure:
            print 'Could not connect to MongoDB!'
            raise

    def _get_exxon_files(self):
        base_dir = os.path.join(here, 'data', 'exxon_assays')
        exxon_files = []

        for root, _dirnames, filenames in os.walk(base_dir):
            for filename in fnmatch.filter(filenames, 'index.txt'):
                exxon_files.append(os.path.join(root, filename))

        return exxon_files

    def finalize_options(self):
        self.client.close()

    def run(self):
        logging.basicConfig(level=logging.INFO)

        if db_name in self.client.database_names():
            confirmation = self.prompt()
            if not confirmation:
                print 'Ok, quitting the database initialization now...'
                return

        self.init_database()
        self.load_database()

    def prompt(self):
        resp = raw_input('This action will permanently delete all data in the '
                         'existing database!\n'
                         'Are you sure you want to re-initialize it? (y/n): ')
        return len(resp) > 0 and resp.lower()[0] == 'y'

    def init_database(self):
        '''
            Initialize the database.
            MongoDB is a bit new to me, but I'm thinking that we could simply
            drop the database if it exists, and then create it along with our
            collections.
        '''
        try:
            if db_name in self.client.database_names():
                print 'Dropping database "{}"...'.format(db_name),
                self.client.drop_database(db_name)
                print 'Dropped'
        except ConnectionFailure:
            print 'Could not connect to MongoDB!'
            raise
        except Exception:
            print 'Failed to drop Oil database!'
            raise

    def load_database(self):
        try:
            from oil_database.scripts.db_initialize import init_db
            init_db(self.settings)
            print 'Oil database successfully generated from file!'
        except Exception:
            print 'Oil database generation failed'
            raise


class PyTest(TestCommand):
    """So we can run tests with ``setup.py test``"""
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
      cmdclass={'make_db': make_db,
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
