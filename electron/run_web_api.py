#!/usr/bin/env python

"""
Startup script for web_api for ADIOS OIl Database
"""

import pyramid.paster
import waitress

pyramid.paster.setup_logging("config:development.ini")

app = pyramid.paster.get_app("config:development.ini")

waitress.serve(app, ...options...)
