#!/usr/bin/env python
import logging
import re
from math import isclose

from adios_db.models.oil.oil import Oil
from adios_db.models.common.measurement import Temperature, Density
from ..v2 import EnvCanadaCsvRecordMapper
from .refcode_lu import reference_codes


logger = logging.getLogger(__name__)


class EnvCanadaCsvRecordMapper1999(EnvCanadaCsvRecordMapper):
    """
    A translation/conversion layer for the Environment Canada imported
    record object.
    Basically, the parser has already got the structure mostly in order,
    but because of the nature of the .csv measurement rows, some re-mapping
    will be necessary to put it in a form that the Oil object expects.
    """
    vs_map = {
        'yes': 'Unknown stability',
        'no': 'Did not form',
        'non': 'Did not form',
        'meso-stable': 'Mesostable',
        'not stable': 'Unstable',
    }

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
                            new_vs = self.vs_map.get(new_vs.lower(), new_vs)
                            new_emul['visual_stability'] = new_vs

                        new_emul['method'] = ', '.join({v['method']
                                                        for v
                                                        in emul.values()
                                                        if hasattr(v, 'method')
                                                        })

                    emulsions[idx] = new_emul

                eb['emulsions'] = [em for em in emulsions if em]

    def remap_distillation_final_bp(self):
        for sample in self.record['sub_samples']:
            dist = sample.get('distillation_data', {})

        final_cut = None
        for i, c in enumerate(dist.get('cuts', [])):
            if 'final_bp' in c:
                final_cut = dist['cuts'].pop(i)
                break  # we will assume there is only one final cut

        if final_cut is not None and 'vapor_temp' in final_cut:
            dist['end_point'] = final_cut['vapor_temp']

    def remap_distillation_sort_by_fraction(self):
        for sample in self.record['sub_samples']:
            dist = sample.get('distillation_data', {})

            if 'cuts' in dist:
                dist['cuts'] = sorted(
                    dist['cuts'],
                    key=lambda c: (c.get('fraction', {}).get('value', None),
                                   c.get('vapor_temp', {}).get('value', None))
                )

    def get_ref_year(self, name, reference):
        """
        Search the name and reference text looking for a year
        """
        years = [int(n) for n in re.compile(r'\b\d{4}\b').findall(name)]

        if len(years) > 0:
            # we would prefer if the year was contained in the name
            return max(years)

        # but if not, we continue our search in the reference text
        years.extend(
            [int(n) for n in re.compile(r'\b\d{4}\b').findall(reference)]
        )

        if len(years) > 0:
            return max(years)
        else:
            return None

    def remap_reference_codes(self):
        """
        The content of the reference will be either a single code or a
        pipe '|' delimited sequence of codes that reference the full title(s)
        of the reference document.  We will convert the sequence of codes
        into a sequence of full titles separated by a newline '\n'.
        """
        ref = self.record['metadata']['reference']
        oil_name = self.record['metadata']['name']
        newref = ''

        if '|' in ref:
            for refcode in ref.split('|'):
                newref += reference_codes.get(refcode, refcode)
                newref += '\n'
        else:
            newref = reference_codes.get(ref, ref)

        # reference needs special treatment
        self.deep_set(self.record, 'metadata.reference', {
            'reference': newref,
            'year': self.get_ref_year(oil_name, newref)
        })

    def remap_oil_api(self):
        if len(self.record['sub_samples']) > 0:
            # API must be determined from a fresh sample.  There is
            # no point in going forward if it is not fresh.
            # The criteria for a fresh sample are:
            # - It has to be the first sample
            # - The fraction weathered should be very close to 0.0
            fresh_sample = self.record['sub_samples'][0]

            try:
                fraction_weathered = (fresh_sample.get('metadata', {})
                                      .get('fraction_weathered', {})
                                      .get('value', None))
            except Exception:
                logger.warning(f'{self.record["oil_id"]}: fresh sample has '
                               'a weird fraction weathered value. '
                               f'{fresh_sample["metadata"]=}')
                return

            if (fraction_weathered is None or
                    not isclose(fraction_weathered, 0.0)):
                return

            api = self.record.get('metadata', {}).get('API', None)

            if api is None:
                # grab the fresh density at 15C and convert
                densities = (fresh_sample.get('physical_properties', {})
                             .get('densities', []))
                api_density = None

                for d in densities:
                    ref_temp = Temperature.from_py_json(d.get('ref_temp', {}))
                    temperature_value = ref_temp.convert_to('C').value

                    if (temperature_value is not None and
                            isclose(temperature_value, 15.0)):
                        api_density = Density.from_py_json(
                            d.get('density', {})
                        ).value
                        break

                if api_density is not None:
                    api_rho = api_density  # g/mL
                    api = 141.5 / api_rho - 131.5

            if api is not None:
                try:
                    self.record['metadata']['API'] = round(api, 2)
                except TypeError:
                    logger.warning(f'oil {self.record["oil_id"]} '
                                   f'failed to set API to {api}')
