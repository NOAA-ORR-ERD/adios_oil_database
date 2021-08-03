import { helper } from '@ember/component/helper';

import Nucos from 'nucos/nucos';


export function getUnitType(unit) {
    if (!unit) {
        return null;
    }

    let compatibleWith = Object.values(Nucos.Converters).filter(c => {
        return c.Synonyms.hasOwnProperty(unit.toLowerCase()
                                         .replace(/[\s.]/g, ''));
    });

    if (compatibleWith.length === 0) {
        throw `'${unit}' is not compatible with any converters`;
    }
    else {
        // There may be multiple converters, but we will just choose the first
        // one.  This may result in the occasional wrong unit type, but it
        // should be sufficient for conversion.
        return compatibleWith[0].Name.toLowerCase().replace(/[\s.]/g, '');
    }
}

export default helper(getUnitType);
