import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class Sulfur extends Component {

    @tracked sulfurContent;

    constructor() {
        super(...arguments);

        let sulfur = this.args.oil.bulk_composition.filter(function(i) {
            return i['name'].toLowerCase() == 'sulfur content';
        });

        if (sulfur.length > 0) {
            this.sulfurContent = sulfur[0].measurement;
        }
    }

    @action
    submit() {
        this.args.submit(this.args.oil);
    }
}
