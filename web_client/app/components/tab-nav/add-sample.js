import Component from '@glimmer/component';
import { action } from "@ember/object";

export default class AddSample extends Component {
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
