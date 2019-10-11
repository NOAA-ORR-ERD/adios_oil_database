import { helper } from '@ember/component/helper';

export function weatheredSamples([oil,
                                  ...rest]) {  // eslint-disable-line no-unused-vars
  let samples = new Set();

  oil.eachAttribute(a => {
    let attr = oil.get(a);
    if (attr &&
        attr.length > 0 &&
        typeof attr['map'] === 'function' &&
        attr.every(i => (i !== null && i['weathering'] !== undefined))) {
      attr.map(i => (samples.add(i.weathering)));
    }
  });
  
  return Array.from(samples);
}

export default helper(weatheredSamples);
