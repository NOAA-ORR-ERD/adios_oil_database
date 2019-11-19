import { helper } from '@ember/component/helper';

export function weatheredSamples([oil,
                                  ...rest]) {  // eslint-disable-line no-unused-vars
  let samples = new Set();

  oil.samples.forEach(s => {
      if (typeof s.sample_id.split('=')[1] === 'undefined') {
          // sample does not fit the 'w=<num>' format, just add the label
          samples.add(s.sample_id);
      }
      else if (isNaN(Number(s.sample_id.split('=')[1]))) {
          // sample fits the 'w=<num>' format, just not a number
          samples.add(s.sample_id.split('=')[1]);          
      }
      else {
          // sample fits the 'w=<num>' format, and is a number
          samples.add(Number(s.sample_id.split('=')[1]));
      }
  });

  return Array.from(samples);
}

export default helper(weatheredSamples);
