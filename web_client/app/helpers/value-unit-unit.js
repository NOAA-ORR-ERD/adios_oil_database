import { helper } from '@ember/component/helper';

export function valueUnitUnit([valueUnitObj,
                               ...rest]) {  // eslint-disable-line no-unused-vars
  if (valueUnitObj == null) {return '';}

  let u = valueUnitObj.unit;
  let sep = ' ';

  // SI Kelvin units don't have a degree, so are not included here.
  let tempUnits = new Set(['F', 'C']);
  let fractionUnits = new Set(['1'])

  if (tempUnits.has(u)) {
    sep = '°';
    return ` ${sep}${u}`;
  }
  else if (fractionUnits.has(u)) {
    return ``;
  }
  else {
    let new_u = u.replace('^2', '\u00B2')
    new_u = new_u.replace('^3', '\u00B3')

    return `${sep}${new_u}`;
  }      
}

export default helper(valueUnitUnit);
