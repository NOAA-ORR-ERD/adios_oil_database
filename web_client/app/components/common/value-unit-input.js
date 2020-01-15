import Component from '@glimmer/component';
import { action } from "@ember/object";
import { valueUnitUnit } from 'ember-oil-db/helpers/value-unit-unit';

export default class ValueUnitInput extends Component {

    constructor() {
        super(...arguments);

        let unitObj = {"unit": this.args.valueUnit};
        this.beaUnit = valueUnitUnit([unitObj]);
    }

    @action
    updateValue() {
        // TODO
    }
    
}