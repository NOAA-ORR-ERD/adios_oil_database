import { helper } from '@ember/component/helper';
import { valueUnitRange } from './value-unit-range';
import { valueUnitScalar } from './value-unit-scalar';


export function valueUnit([valueUnitObj, tol,
                           ...rest]) {  // eslint-disable-line no-unused-vars
  if (valueUnitObj == null) {
      return '';
  }
  else if (Number.isFinite(valueUnitObj.value)) {
      return valueUnitScalar([valueUnitObj, tol]);
  }
  else {
      return valueUnitRange([valueUnitObj, tol]);
  }
}

export default helper(valueUnit);
