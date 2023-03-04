#!/usr/bin/env python
import logging

from adios_db.models.oil.oil import Oil
from ..v2 import EnvCanadaCsvRecordMapper

import pdb
from pprint import pprint

logger = logging.getLogger(__name__)


class EnvCanadaCsvRecordMapper1999(EnvCanadaCsvRecordMapper):
    """
    A translation/conversion layer for the Environment Canada imported
    record object.
    Basically, the parser has already got the structure mostly in order,
    but because of the nature of the .csv measurement rows, some re-mapping
    will be necessary to put it in a form that the Oil object expects.
    """
    def remap_emulsions(self):
        for sample in self.record['sub_samples']:
            eb = sample.get('environmental_behavior', {})
            emulsions = eb.get('emulsions', [])

            if emulsions:
                for idx, emul in enumerate(emulsions):
                    if len({v.get('ref_temp', {}).get('value', None)
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
                                                        in emul.values()
                                                        if hasattr(v, 'method')
                                                        })

                    emulsions[idx] = new_emul

                eb['emulsions'] = [em for em in emulsions if em]

    def remap_final_bp(self):
        for sample in self.record['sub_samples']:
            dist = sample.get('distillation_data', {})

        final_cut = None
        for i, c in enumerate(dist.get('cuts', [])):
            if 'final_bp' in c:
                final_cut = dist['cuts'].pop(i)
                break  # we will assume there is only one final cut

        if final_cut is not None:
            dist['end_point'] = final_cut['vapor_temp']
