import Component from '@ember/component';

export default Component.extend({
    didReceiveAttrs() {
        this._super(...arguments);

        let weathered = this.get('weathered');
        if (weathered === 0) {
            weathered = weathered.toFixed(1);
        }

        let sample = this.get('oil').samples.find( (s) => {
            return s.sample_id === weathered;
        });

        if (typeof sample === 'undefined') {
            sample = this.get('oil').samples.find( (s) => {
                return s.sample_id === `w=${weathered}`;
            });
        }

        this.set('sample', sample);
      },
});
