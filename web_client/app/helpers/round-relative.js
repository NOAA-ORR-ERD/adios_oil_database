import { helper } from '@ember/component/helper';

export function roundRelative([num,
                               tol,
                               ...rest]) {  // eslint-disable-line no-unused-vars
  if (num === 0) {
    return 0.0;
  }
  else if (num > 1.0) {
    return Math.round(num * 10 ** tol) / 10 ** tol;
  }
  else if (num) {
    let scale = 10 ** (tol - 1 - Math.floor(Math.log10(Math.abs(num))));
    return Math.round(num * scale) / scale;
  }
  else {
    return num;  // probably undefined
  }
}

export default helper(roundRelative);
