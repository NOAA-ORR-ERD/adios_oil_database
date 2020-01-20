import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import { valueUnitUnit } from 'ember-oil-db/helpers/value-unit-unit';

export default class ValueUnitInput extends Component {
    @tracked valueObject = {};

    constructor() {
        super(...arguments);

        let unitObj = {"unit": this.args.valueUnit};
        this.beaUnit = valueUnitUnit([unitObj]);
    }

    @action
    updateValue(e) {
        if(Number.isNaN(parseFloat(e.target.value))) {
            this.valueObject = null;
        } else {
            this.valueObject.value = parseFloat(e.target.value);
            this.valueObject.unit = this.args.valueUnit;
        }
        this.args.submit(this.valueObject);
    }
    
}