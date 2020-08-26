import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";
import { valueUnitUnit } from 'ember-oil-db/helpers/value-unit-unit';

export default class ValueUnitInput extends Component {
    @tracked valueObject = {};

    constructor() {
        super(...arguments);

        this.valueObject = this.args.valueObject;

        let unitObj = {"unit": this.args.valueUnit};
        this.beaUnit = valueUnitUnit([unitObj]);
    }

    @action
    updateValue(e) {
        if(Number.isNaN(parseFloat(e.target.value))) {
            this.valueObject = null;
        } else {
            this.valueObject = {
                value: parseFloat(e.target.value),
                unit: this.args.valueUnit
            };
        }

        Object.entries(this.valueObject).forEach(([key, item]) => {
            set(this.args.valueObject, key, item);
        });

        this.args.submit(this.valueObject);
    }
}
