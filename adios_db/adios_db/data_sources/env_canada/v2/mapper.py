#!/usr/bin/env python
import logging

from adios_db.models.oil.oil import Oil
from adios_db.data_sources.mapper import MapperBase

logger = logging.getLogger(__name__)


class EnvCanadaCsvRecordMapper(MapperBase):
    """
    A translation/conversion layer for the Environment Canada imported
    record object.
    Basically, the parser has already got the structure mostly in order,
    but because of the nature of the .csv measurement rows, some re-mapping
    will be necessary to put it in a form that the Oil object expects.
    """
    def __init__(self, record):
        """
        :param record: A parsed object representing a single oil or
                       refined product.
        :type record: A record parser object.
        """
        if hasattr(record, 'oil_obj'):
            self.record = record.oil_obj
        else:
            raise ValueError(f'{self.__class__.__name__}(): '
                             'invalid parser passed in')

        method_list = [attr for attr in dir(self)
                       if callable(getattr(self, attr))
                       and attr.startswith('remap_') is True]
        self.reorder_methods(method_list)

        for method in method_list:
            getattr(self, method)()

    def reorder_methods(self, methods):
        '''
        Generally the remap_*() methods are supposed to be executable in
        any order, but there could be a situation where a particular
        method needs to run before another.

        This method receives a list of method names, and modifies the list
        in-place.

        Example:

            try:
                # move the method 'remap_method' to the front of the list
                methods.insert(0, methods.pop(methods.index('remap_method')))
            except ValueError:
                # Raise a warning that the method could not be reordered.
                pass
        '''
        pass

    def remap_SARA(self):
        for sample in self.record['sub_samples']:
            sara = sample.get('SARA', None)

            if sara is not None:
                new_sara = {k: v['measurement'] for k, v in sara.items()}
                new_sara['method'] = ', '.join({v['method']
                                                for v in sara.values()
                                                if 'method' in v})
                sample['SARA'] = new_sara

    def remap_ESTS_evaporation(self):
        for sample in self.record['sub_samples']:
            eb = sample.get('environmental_behavior', {})
            ests_evap = eb.get('ests_evaporation_test', None)

            if ests_evap is not None:
                new_ests_evap = {self.slugify(o['equation']): o['measurement']
                                 for o in ests_evap}
                new_ests_evap['method'] = ', '.join({o['method']
                                                     for o in ests_evap
                                                     if 'method' in o})
                eb['ests_evaporation_test'] = new_ests_evap

    def remap_adhesion(self):
        for sample in self.record['sub_samples']:
            eb = sample.get('environmental_behavior', {})
            adhesion = eb.get('adhesion', None)

            if adhesion is not None:
                eb['adhesion'] = adhesion['adhesion']

    def remap_emulsions(self):
        for sample in self.record['sub_samples']:
            eb = sample.get('environmental_behavior', {})
            emulsions = eb.get('emulsions', [])

            if emulsions:
                for idx, emul in enumerate(emulsions):
                    if len({v['age']['value'] for v in emul.values()}) > 1:
                        raise ValueError('Emulsion has multiple ages')

                    if len({v['ref_temp']['value']
                            for v in emul.values()}) > 1:
                        raise ValueError('Emulsion has multiple '
                                         'reference temperatures')

                    new_emul = {}

                    for k, v in emul.items():
                        if v['measurement']['value'] is not None:
                            # we have something valid
                            new_emul[k] = v['measurement']

                    if new_emul:
                        # it's not empty.
                        ref_temp = (emul.get('visual_stability', {})
                                    .get('ref_temp', None))
                        if ref_temp:
                            new_emul['ref_temp'] = ref_temp

                        age = (emul.get('visual_stability', {})
                               .get('age', None))
                        if age:
                            new_emul['age'] = age

                        new_vs = (new_emul.pop('visual_stability', {})
                                  .get('value', None))
                        if new_vs is not None:
                            new_emul['visual_stability'] = new_vs

                        new_emul['method'] = ', '.join({v['method']
                                                        for v
                                                        in emul.values()})

                    emulsions[idx] = new_emul

                eb['emulsions'] = [em for em in emulsions if em]

    def remap_interfacial_tension(self):
        for sample in self.record['sub_samples']:
            phys = sample.get('physical_properties', {})
            ifts = (phys.get('interfacial_tension', []))

            phys['interfacial_tension_water'] = [
                t for t in ifts if t['interface'] == 'water'
            ]
            phys['interfacial_tension_seawater'] = [
                t for t in ifts if t['interface'] == 'seawater'
            ]

    def remap_cuts(self):
        for sample in self.record['sub_samples']:
            cuts = sample.get('distillation_data', {}).get('cuts', None)
            end_point = (sample.get('distillation_data', {})
                         .get('end_point', None))

            if cuts:
                method_names = ', '.join({c.get('method', '') for c in cuts})
                [c.pop('method', '') for c in cuts]

                sample['distillation_data']['method'] = method_names
                sample['distillation_data']['type'] = 'mass fraction'

            if end_point:
                end_point = end_point['measurement']
                sample['distillation_data']['end_point'] = end_point

    def remap_ESTS_hydrocarbon_fractions(self):
        for sample in self.record['sub_samples']:
            ests_fractions = sample.get('ESTS_hydrocarbon_fractions', {})
            gc_tph = ests_fractions.get('GC_TPH', [])
            saturates = ests_fractions.get('saturates', [])
            aromatics = ests_fractions.get('aromatics', [])

            methods = ', '.join({f.get('method', '')
                                 for f in gc_tph + saturates + aromatics})

            ests_fractions['method'] = methods

            for f in gc_tph + saturates + aromatics:
                f.pop('method', None)

    def remap_CCME(self):
        for sample in self.record['sub_samples']:
            ccme = sample.get('CCME', [])

            new_ccme = {f['name'][-2:]: f['measurement'] for f in ccme}
            new_ccme['method'] = ', '.join({f.get('method', '') for f in ccme})

            sample['CCME'] = new_ccme

    @property
    def oil_id(self):
        return self.record['oil_id']

    def py_json(self):
        rec = Oil.from_py_json(self.record)

        return rec.py_json()
