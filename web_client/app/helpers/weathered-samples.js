import { helper } from '@ember/component/helper';

export function weatheredSamples([oil,
                                  ...rest]) {  // eslint-disable-line no-unused-vars
  let samples = new Set();

  oil.samples.forEach(s => {
      samples.add([s.name, s.short_name]);
  });

  return Array.from(samples);
}

export default helper(weatheredSamples);
