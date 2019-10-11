import { helper } from '@ember/component/helper';
import { roundRelative } from './round-relative';
import { valueUnitUnit } from './value-unit-unit';

export function valueUnitScalar([valueUnitObj, tol,
                                 ...rest]) {  // eslint-disable-line no-unused-vars
  if (valueUnitObj == null) {return '';}

  let v = roundRelative([valueUnitObj.value, tol]);
  let u = valueUnitUnit([valueUnitObj]);

  return `${v}${u}`;
}

export default helper(valueUnitScalar);
