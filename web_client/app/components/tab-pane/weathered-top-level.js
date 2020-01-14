import Component from '@ember/component';

export default Component.extend({
    didReceiveAttrs() {
        this._super(...arguments);

        let sampleName = this.get('sampleName');
        let samples = this.get('oil').samples;

        let sample = samples.find( (s) => {
            return s.name === sampleName;
        });

        // get an index of the current sample - to use one for component ID
        let sampleIndex = this.get('oil').samples.findIndex(
            xSample => xSample.name === sampleName);

        this.set('sample', sample);
        this.set('sampleIndex', sampleIndex);
    },

    actions: {
        submitSample(sample) {
            {{debugger}}
            let oil = this.get('oil');
            // let samples =  oil.samples;
            // samples[this.sampleIndex] = sample;
            // oil.set('samples', samples);
            this.submit(oil);
        }
    }
});
