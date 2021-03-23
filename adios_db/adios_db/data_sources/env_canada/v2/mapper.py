#!/usr/bin/env python
import logging

from adios_db.models.oil.oil import Oil
from adios_db.data_sources.mapper import MapperBase


logger = logging.getLogger(__name__)


class EnvCanadaCsvRecordMapper(MapperBase):
    '''
        A translation/conversion layer for the Environment Canada imported
        record object.
        Basically, the parser has already got the structure mostly in order,
        but because of the nature of the .csv measurement rows, some re-mapping
        will be necessary to put it in a form that the Oil object expects.
    '''
    def __init__(self, record):
        '''
            :param record: A parsed object representing a single oil or
                           refined product.
            :type record: A record parser object.
        '''
        if hasattr(record, 'oil_obj'):
            self.record = record.oil_obj
        else:
            raise ValueError(f'{self.__class__.__name__}(): '
                             'invalid parser passed in')

        self.remap_SARA()
        self.remap_ESTS_evaporation()
        self.remap_adhesion()
        self.remap_emulsions()
        self.remap_interfacial_tension()
        self.remap_cuts()

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

                    emulsions[idx] = new_emul

                eb['emulsions'] = [em for em in emulsions if em]

    def remap_interfacial_tension(self):
        pass

    def remap_cuts(self):

        for sample in self.record['sub_samples']:
            cuts = sample.get('distillation_data', {}).get('cuts', None)
            end_point = (sample.get('distillation_data', {})
                         .get('end_point', None))

            if cuts:
                method_names = ', '.join({c['method'] for c in cuts})

                sample['distillation_data']['method'] = method_names
                sample['distillation_data']['type'] = 'mass fraction'

            if end_point:
                end_point = end_point['measurement']
                sample['distillation_data']['end_point'] = end_point

    @property
    def oil_id(self):
        return self.record['oil_id']

    def py_json(self):
        rec = Oil.from_py_json(self.record)

        return rec.py_json()
