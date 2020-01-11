import { helper } from '@ember/component/helper';
import { valueUnitRange } from './value-unit-range';
import { valueUnitScalar } from './value-unit-scalar';


export function valueUnit([valueUnitObj, tol, hideUnit,
                           ...rest]) {  // eslint-disable-line no-unused-vars
  if (valueUnitObj == null) {
      return '';
  }
  else if (Number.isFinite(valueUnitObj.value)) {
      return valueUnitScalar([valueUnitObj, tol, hideUnit]);
  }
  else {
      return valueUnitRange([valueUnitObj, tol, hideUnit]);
  }
}

export default helper(valueUnit);
