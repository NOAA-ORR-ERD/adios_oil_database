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
        {{debugger}}
        if(isNaN(e.target.value)) {
            this.valueObject = undefined;
        } else {
            this.valueObject.value = Number(e.target.value);
            this.valueObject.unit = this.args.valueUnit;
        }
        this.args.submit(this.valueObject);
    }
    
}