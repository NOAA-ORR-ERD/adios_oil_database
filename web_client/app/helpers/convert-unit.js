import $ from 'jquery';
import { helper } from '@ember/component/helper';

import Nucos from 'nucos/nucos';


export function convertUnit([valueUnitObj,
                             newUnit,
                             unitType,
                             ...rest]) {  // eslint-disable-line no-unused-vars
  if (!valueUnitObj) {
    return valueUnitObj;
  }

  let copyObj = $.extend(true, {}, valueUnitObj);

  let compatibleWithIn = Object.values(Nucos.Converters).filter(c => {
    return c.Synonyms.hasOwnProperty(copyObj.unit.toLowerCase().replace(/\s/g,''));
  });

  if (compatibleWithIn.length === 0) {
    throw `Input unit ${copyObj.unit} is not compatible with any converters`;
  }

  let compatibleWithOut = compatibleWithIn.filter(c => {
    return c.Synonyms.hasOwnProperty(newUnit.toLowerCase().replace(/\s/g,''));
  });

  if (compatibleWithOut.length === 1) {
    // This is the only converter we can use, so ignore the unitType
    let converter = compatibleWithOut[0];

    if (copyObj.value) {
      copyObj.value = Nucos.convert(converter.Name,
                                    copyObj.unit,
                                    newUnit,
                                    copyObj.value);
    }

    if (copyObj.min_value) {
      copyObj.min_value = Nucos.convert(converter.Name,
                                        copyObj.unit,
                                        newUnit,
                                        copyObj.min_value);
    }

    if (copyObj.max_value) {
      copyObj.max_value = Nucos.convert(converter.Name,
                                        copyObj.unit,
                                        newUnit,
                                        copyObj.max_value);
    }

    copyObj.unit = newUnit;
  }
  else if (compatibleWithOut.length > 1) {
    // multiple converters available.  Do they match our unitType?
    let compatibleWithUnitType = compatibleWithOut.filter(c => {
      return c.Name === unitType;
    });

    if (compatibleWithUnitType.length === 1) {
      let converter = compatibleWithUnitType[0];

      if (copyObj.value) {
        copyObj.value = Nucos.convert(converter.Name,
                                      copyObj.unit,
                                      newUnit,
                                      copyObj.value);
      }

      if (copyObj.min_value) {
        copyObj.min_value = Nucos.convert(converter.Name,
                                          copyObj.unit,
                                          newUnit,
                                          copyObj.min_value);
      }

      if (copyObj.max_value) {
        copyObj.max_value = Nucos.convert(converter.Name,
                                          copyObj.unit,
                                          newUnit,
                                          copyObj.max_value);
      }

      copyObj.unit = newUnit;
    }
    else {
      throw `Specified unit type ${unitType} is not compatible with input unit`;
    }
  }
  else {
    throw `New unit ${newUnit} is not compatible with input unit ${valueUnitObj.unit}`;
  }

  return copyObj;
}

export default helper(convertUnit);
