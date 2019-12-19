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
  
  if (!isNaN(parseFloat(min)) && isFinite(min) &&
      !isNaN(parseFloat(max)) && isFinite(max) &&
      min === max) {
    valueUnitObj.value = valueUnitObj.min_value;
    return `${min}${unit}`
  }
  else if (!isNaN(parseFloat(min)) && isFinite(min) &&
           !isNaN(parseFloat(max)) && isFinite(max)) {
    return `[${min}\u2192${max}]${unit}`;
  }
  else if (!isNaN(parseFloat(min)) && isFinite(min)) {
    return `>${min}${unit}`;
  }
  else if (!isNaN(parseFloat(max)) && isFinite(max)) {
    return `<${max}${unit}`;
  }

  return null;
}

export default helper(valueUnitRange);
