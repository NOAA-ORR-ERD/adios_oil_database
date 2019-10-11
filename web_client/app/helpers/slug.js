import { helper } from '@ember/component/helper';
import slugify from 'ember-slugify';

export function slug([input,
                      ...rest]) {  // eslint-disable-line no-unused-vars
  return slugify(input.toString());
}

export default helper(slug);
