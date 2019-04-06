import logging

import numpy as np

from pymongo.errors import DuplicateKeyError
from pymodm.errors import ValidationError

from oil_database.util.term import TermColor as tc
from oil_database.util.estimations import api_from_density

from oil_database.models.noaa_fm import ImportedRecord
from oil_database.models.ec_imported_rec import ECImportedRecord

from oil_database.models.oil import Oil

from oil_database.data_sources.env_canada import EnvCanadaAttributeMapper
from oil_database.data_sources.noaa_fm import OilLibraryAttributeMapper

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)

logger = logging.getLogger(__name__)


class OilRejected(Exception):
    '''
        Custom exception for Oil initialization that we can raise if we
        decide we need to reject an oil record for any reason.
    '''
    def __init__(self, message, oil_name, *args):
        # without this you may get DeprecationWarning
        self.message = message

        # Special attribute you desire with your Error,
        # perhaps the value that caused the error?:
        self.oil_name = oil_name

        # allow users initialize misc. arguments as any other builtin Error
        super(OilRejected, self).__init__(message, oil_name, *args)

    def __repr__(self):
        return '{0}(oil={1}, errors={2})'.format(self.__class__.__name__,
                                                 self.oil_name,
                                                 self.message)


def process_oils():
    '''
        The idea is that an imported record contains data items from a source
        that are presumed to be the measured properties of the petroleum
        product.  We want it to be easy to analyze the original source
        information, so we want to keep this around unmodified.

        We also want to have an oil table that contains all records.
    '''
    logger.info('Adding Oil objects...')
    for rec in ImportedRecord.objects.all():
        try:
            add_oil(OilLibraryAttributeMapper(rec))
        except OilRejected as e:
            logger.warning(repr(e))
        except ValidationError as e:
            logger.warning(u'validation failed for {}: {}'
                           .format(tc.change(rec.oil_id, 'red'), e))
        except DuplicateKeyError as e:
            logger.warning(u'duplicate fields for {}: {}'
                           .format(tc.change(rec.oil_id, 'red'), e))

    logger.info('Adding Environment Canada Oil objects...')
    for rec in ECImportedRecord.objects.all():
        try:
            add_oil(EnvCanadaAttributeMapper(rec))
        except OilRejected as e:
            logger.warning(repr(e))
        except ValidationError as e:
            logger.warning(u'validation failed for {}: {}'
                           .format(tc.change(rec.oil_id, 'red'), e))
        except DuplicateKeyError as e:
            logger.warning(u'duplicate fields for {}: {}'
                           .format(tc.change(rec.oil_id, 'red'), e))


def add_oil(mapper):
    '''
        Originally, we wanted to populate the oil table with generalized oil
        objects that had rich sets of properties, including estimations of
        any necessary properties that were missing.

        Our strategy has changed a bit, however.  We still have a generalized
        oil object, but we will forego the estimations.

        Later, when we want to use a richly constructed record, we will perform
        estimations on-demand.
    '''
    print ('\n\nAdding {}: id = {}, name = {}'
           .format(mapper.record.__class__.__name__,
                   mapper.oil_id, mapper.name))

    oil_obj = Oil.from_record_parser(mapper)

    print 'oil.conradson:'
    for a in oil_obj.conradson:
        print '\t', a

    # TODO: We will need to reject oils that are not good before deciding to
    #       save them.  Just save them for now though.

    oil_obj.save()


#
#
# ### Oil Quality checks
#
#
def reject_imported_record_if_requirements_not_met(imported_rec):
    '''
        Here, we have an imported oil record for which we would like to
        make estimations.  For this to happen, certain requirements need
        to be met.  Otherwise, we reject the oil without performing
        estimations.
    '''
    errors = []

    if manually_rejected(imported_rec):
        errors.append('Imported Record was manually rejected')

    if not has_product_type(imported_rec):
        errors.append('Imported Record has no product type')

    if not has_api_or_densities(imported_rec):
        errors.append('Imported Record has no density information')

    if not has_viscosities(imported_rec):
        errors.append('Imported Record has no viscosity information')

    if not has_distillation_cuts(imported_rec):
        errors.append('Imported Record has insufficient cut data')

    if len(errors) > 0:
        try:
            oil_id = imported_rec.adios_oil_id
        except AttributeError:
            oil_id = imported_rec.oil_id

        raise OilRejected(errors, oil_id)


def manually_rejected(imported_rec):
    '''
        This list was initially compiled to try and fix some anomalies
        that were showing up in the oil query form.

        When we update the source file that provides our imported record
        data, we should revisit this list.
        We should also revisit this list as we add methods to detect flaws
        in our oil record.
    '''
    try:
        oil_id = imported_rec.adios_oil_id
    except AttributeError:
        oil_id = imported_rec.oil_id

    if oil_id in (None,):
        return True

    return False


def has_product_type(imported_rec):
    '''
        In order to perform estimations, we need to determine if we are
        dealing with a crude or refined oil product.  We cannot continue
        if this information is missing.
    '''
    if (imported_rec.product_type is not None and
            imported_rec.product_type.lower() in ('crude', 'refined')):
        return True

    return False


def has_api_or_densities(imported_rec):
    '''
        In order to perform estimations, we need to have at least one
        density measurement.  We cannot continue if this information
        is missing.
        This is just a primitive test, so we do not evaluate the quantities,
        simply that some kind of value exists.
    '''
    if has_api(imported_rec):
        return True
    elif len(imported_rec.densities) > 0:
        return True
    else:
        return False


def has_api(imported_rec):
    '''
        Env Canada record has multiple weathered APIs, so we need to account
        for that.
    '''
    try:
        apis = imported_rec.api
    except Exception:
        apis = imported_rec.apis

    if (apis is not None and apis != []):
        return True
    else:
        return False


def has_viscosities(imported_rec):
    '''
        In order to perform estimations, we need to have at least one
        viscosity measurement.  We cannot continue if this information
        is missing.
        This is just a primitive test, so we do not evaluate the quantities,
        simply that some kind of value exists.
    '''
    if hasattr(imported_rec, 'kvis') and len(imported_rec.kvis) > 0:
        return True
    elif hasattr(imported_rec, 'dvis') and len(imported_rec.dvis) > 0:
        return True
    else:
        return False


def has_distillation_cuts(imported_rec):
    '''
        - In order to perform estimations on a refined product, we need to have
          at least three distillation cut measurements.  We cannot continue
          if this information is missing.
        - For crude oil products, we can estimate cut information from its
          API value if the cuts don't exist.
        - If we have no cuts and no API, we can still estimate cuts by
          converting density to API, and then API to cuts.
        - This is just a primitive test, so we do not evaluate the quantities,
          simply that some kind of value exists.
    '''
    if (imported_rec.product_type is not None and
            imported_rec.product_type.lower() == 'crude'):
        if (len(imported_rec.cuts) >= 3 or
                has_api_or_densities(imported_rec)):
            return True  # cuts can be estimated if not present
        else:
            return False
    else:
        if len(imported_rec.cuts) >= 3:
            return True
        else:
            return False


def has_densities_below_pour_point(imported_rec):
    '''
        This may be presumptuous, but I believe the volumetric coefficient
        that we use for calculating densities at temperature are probably for
        oils in the liquid phase.  So we would like to check if any
        densities in our oil fall below the pour point.

        Note: Right now we won't worry about estimating the pour point
              if the pour point data points don't exist for the record,
              then we will assume that our densities are probably fine.
    '''
    try:
        pp_max = imported_rec.pour_point_max_k
        pp_min = imported_rec.pour_point_min_k
        pour_point = min([pp for pp in (pp_min, pp_max) if pp is not None])
    except (ValueError, TypeError):
        pour_point = None

    if pour_point is None:
        return False
    else:
        rho_temps = [d.ref_temp_k for d in imported_rec.densities
                     if d.ref_temp_k is not None]
        if imported_rec.api is not None:
            rho_temps.append(288.15)

        if any([(t < pour_point) for t in rho_temps]):
            try:
                oil_id = imported_rec.adios_oil_id
            except AttributeError:
                oil_id = imported_rec.oil_id

            print ('\toil_id: {}, pour_point: {}, rho_temps: {}, lt: {}'
                   .format(oil_id, pour_point, rho_temps,
                           [(t < pour_point) for t in rho_temps]))
            return True


def reject_oil_if_bad(oil):
    '''
        Here, we have an oil in which all estimations have been made.
        We will now check it to see if there are any detectable flaws.
        If any flaw is detected, we will raise the OilRejected exception.
        All flaws will be compiled into a list of error messages to be passed
        into the exception.
    '''
    errors = []

    if not oil_has_kvis(oil):
        errors.append('Oil has no kinematic viscosities')

    if oil_has_duplicate_cuts(oil):
        errors.append('Oil has duplicate cuts')

    if oil_has_heavy_sa_components(oil):
        errors.append('Oil has heavy SA components')

    if not oil_api_matches_density(oil):
        errors.append('Oil API does not match its density')

    if len(errors) > 0:
        try:
            oil_id = oil.adios_oil_id
        except AttributeError:
            oil_id = oil.oil_id

        raise OilRejected(errors, oil_id)


def oil_has_kvis(oil):
    '''
        Our oil record should have at least one kinematic viscosity when
        estimations are complete.
    '''
    if len(oil.kvis) > 0:
        return True
    else:
        return False


def oil_has_duplicate_cuts(oil):
    '''
        Some oil records have been found to have distillation cuts with
        duplicate vapor temperatures, and the fraction that should be chosen
        at that temperature is ambiguous.
    '''
    unique_temps = set([o.vapor_temp_k for o in oil.cuts])

    if len(oil.cuts) != len(unique_temps):
        return True
    else:
        return False


def oil_has_heavy_sa_components(oil):
    '''
        Some oil records have been found to have Saturate & Asphaltene
        densities that were calculated to be heavier than the Resins &
        Asphaltenes.
        This is highly improbable and indicates the record has problems
        with its imported data values.
    '''
    resin_rho = [d.kg_m_3 for d in oil.sara_densities
                 if d.sara_type == 'Resins']

    if len(resin_rho) == 0:
        resin_rho = 1100.0
    else:
        resin_rho = np.max((resin_rho[0], 1100.0))

    for d in oil.sara_densities:
        if d.sara_type in ('Saturates', 'Aromatics'):
            if d.kg_m_3 > resin_rho:
                return True

    return False


def oil_api_matches_density(oil):
    '''
        The oil API should pretty closely match its density at 15C.

        Note: we will need to rework this function.  Return True for now.
    '''
    return True
