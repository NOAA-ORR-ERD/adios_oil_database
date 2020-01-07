import Component from '@ember/component';
import EmberObject from '@ember/object';
import { action } from "@ember/object";


export default Component.extend({

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
});
