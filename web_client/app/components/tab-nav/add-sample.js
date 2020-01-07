import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class AddSample extends Component {
    @tracked sampleType = 0;

    SampleTypes = {
            weathered: 0,
            distillate: 1,
            nameOnly: 2
    };

    @action
    updateSampleType(choice) {
        console.log('changing subsample type choice',
                    'from', this.sampleType,
                    'to', choice.target.value);

        this.sampleType = Number(choice.target.value);
    }

    @action
    addSample() {
        console.log('Adding sample...');

        let oil = this.get('oil');
        let samples = oil.get('samples');

        samples.pushObject({
            name: 'new sample',
            short_name: 'new sample'
        });

        this.submit(oil);
    }

};
