import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class Wax extends Component {

    @tracked waxContent;

    constructor() {
        super(...arguments);

        let wax = this.args.oil.bulk_composition.filter(function(i) {
            return i['name'].toLowerCase() == 'wax content';
        });

        if (wax.length > 0) {
            this.waxContent = wax[0].measurement;
        }
    }

    @action
    submit() {
        this.args.submit(this.args.oil);
    }
}
