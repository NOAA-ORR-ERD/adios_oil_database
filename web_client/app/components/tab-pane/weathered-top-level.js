import Component from '@ember/component';

export default Component.extend({
    didReceiveAttrs() {
        this._super(...arguments);

        let sampleName = this.get('sampleName');

        let sample = this.get('oil').samples.find( (s) => {
            return s.name === sampleName;
        });

        this.set('sample', sample);
      },
});
