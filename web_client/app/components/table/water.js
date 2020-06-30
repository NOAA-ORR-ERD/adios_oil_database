import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class Water extends Component {

    @tracked waterContent;

    constructor() {
        super(...arguments);

        let water = this.args.oil.bulk_composition.filter(function(i) {
            return i['name'].toLowerCase() == 'water content';
        });

        if (water.length > 0) {
            this.waterContent = water[0].measurement;
        }
    }

    @action
    submit() {
        this.args.submit(this.args.oil);
    }
}
