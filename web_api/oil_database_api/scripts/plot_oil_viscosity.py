#!/usr/bin/env python

import sys
import os
import transaction

import numpy as np

from matplotlib import pyplot as plt

from pyramid.paster import get_appsettings, setup_logging
from pyramid.scripts.common import parse_vars

from pymodm.errors import DoesNotExist

from oil_database.util.db_connection import connect_modb


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: {0} <config_uri> <adios oil id>\n'
          '(example: "{0} development.ini adios_id=AD00047")'.format(cmd))
    sys.exit(1)


def plot_oil_viscosities(settings):
    if 'adios_id' not in settings:
        raise ValueError('adios_id setting is required.')
    adios_id = settings['adios_id']

    try:
        # in SQLAlchemy, we would query a single result with the .one()
        # function.  This would raise an exception if there were either too
        # few or too many results.
        #
        # PyMODM does this through its get() function
        oil_obj = Oil.objects.get({'adios_oil_id': adios_id})
    except DoesNotExist:
        raise DoesNotExist('No Oil was found matching adios_id {0}'
                           .format(adios_id))

    if oil_obj:
        print 'Our oil object: %s' % (oil_obj)

        print '\nOur viscosities:'
        print [v for v in oil_obj.kvis]

        print '\nOur unweathered viscosities (m^2/s, Kdegrees):'
        vis = [v for v in oil_obj.kvis if v.weathering <= 0.0]
        print vis
        for i in [(v.m_2_s, v.ref_temp_k, v.weathering)
                  for v in vis]:
            print i

        x = np.array([v.ref_temp_k for v in vis]) - 273.15
        y = np.array([v.m_2_s for v in vis])
        xmin = x.min()
        xmax = x.max()
        xpadding = .5 if xmax == xmin else (xmax - xmin) * .3
        ymin = y.min()
        ymax = y.max()
        ypadding = (ymax / 2) if ymax == ymin else (ymax - ymin) * .3
        plt.plot(x, y, 'ro')
        plt.xlabel(r'Temperature ($^\circ$C)')
        plt.ylabel('Unweathered Kinematic Viscosity (m$^2$/s)')
        plt.yscale('log', subsy=[2, 3, 4, 5, 6, 7, 8, 9])
        plt.grid(True)
        plt.axis([xmin - xpadding, xmax + xpadding, 0, ymax + ypadding])

        # now we add the annotations
        for xx, yy in np.vstack((x, y)).transpose():
            print (xx, yy)
            if xx > x.mean():
                xalign = -xpadding / 3
            else:
                xalign = xpadding / 3
            yalign = ypadding / 3

            plt.annotate('(%s$^\circ$C, %s m$^2$/s)' % (xx, yy),
                         xy=(xx + (xalign / 10),
                             yy + (yalign / 10)),
                         xytext=(xx + xalign, yy + yalign),
                         arrowprops=dict(facecolor='black',
                                         shrink=0.01),
                         fontsize=9)
        plt.show()


def main(argv=sys.argv, proc=plot_oil_viscosities):
    if len(argv) < 3:
        usage(argv)

    config_uri = argv[1]
    options = parse_vars(argv[2:])

    setup_logging(config_uri)
    settings = get_appsettings(config_uri,
                               name='oil_database_api',
                               options=options)

    # One more time, this is annoying.  We have to connect to *something*
    # in order for us to even import our model classes.
    connect_modb(settings)
    global Oil
    from oil_database.models.oil import Oil

    try:
        proc(settings)
    except Exception:
        print "{0} FAILED\n".format(proc)
        raise
