import Component from '@ember/component';
import { action } from "@ember/object";

export default Component.extend({
    @action
    removeSample(sampleIndex) {
        let oil = this.get('oil');
        let samples = oil.get('samples');

        // remove the sample
        console.log('Removing sample...', sampleIndex);
        samples.splice(sampleIndex, 1);
        oil.set('samples', samples);

        this.submit(oil);
    }

});
