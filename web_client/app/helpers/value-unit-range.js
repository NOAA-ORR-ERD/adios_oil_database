import { helper } from '@ember/component/helper';
import { roundRelative } from './round-relative';
import { valueUnitUnit } from './value-unit-unit';


export function valueUnitRange([valueUnitObj, tol,
                                ...rest]) {  // eslint-disable-line no-unused-vars
  if (valueUnitObj == null) {
      return '';
  }

  let unit = valueUnitUnit([valueUnitObj]);
  let min = roundRelative([valueUnitObj.min_value, tol]);
  let max = roundRelative([valueUnitObj.max_value, tol]);
  
  if (min && max && min === max) {
    valueUnitObj.value = valueUnitObj.min_value;
    return `${min}${unit}`
  }
  else if (min && max) {
    return `[${min}\u2192${max}]${unit}`;
  }
  else if (min) {
    return `>${min}${unit}`;
  }
  else if (max) {
    return `<${max}${unit}`;
  }

  return null;
}

export default helper(valueUnitRange);
