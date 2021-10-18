import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";
import { valueUnitUnit } from 'adios-db/helpers/value-unit-unit';
import { getUnitType } from 'adios-db/helpers/get-unit-type';


export default class ValueUnitInput extends Component {
    @tracked valueObject = {};

    constructor() {
        super(...arguments);

        this.valueObject = this.args.valueObject;

        let unitObj = {"unit": this.args.valueUnit};
        this.beaUnit = valueUnitUnit([unitObj]);
        
        this.editUnit = this.args.editUnit;
    }

    @action
    updateValue(e) {
        if (Number.isNaN(parseFloat(e.target.value))) {
            this.valueObject = {};
            Object.keys(this.args.valueObject).forEach((key) => {
                delete this.args.valueObject[key];
            });
        }
        else if (this.args.valueUnitType === 'unknown') {
            alert('Updating Unitted Value: ' +
                  `The unit type "${this.args.valueUnitType}" is invalid.`);
            this.valueObject = {};
            Object.keys(this.args.valueObject).forEach((key) => {
                delete this.args.valueObject[key];
            });
        }
        else {
            let unitType;

            if (this.args.valueUnitType) {
                unitType = this.args.valueUnitType;
            }
            else {
                unitType = getUnitType(this.args.valueUnit);
            }

            this.valueObject = {
                value: parseFloat(e.target.value),
                unit: this.args.valueUnit,
                unit_type: unitType
            };

            Object.entries(this.valueObject).forEach(([key, item]) => {
                set(this.args.valueObject, key, item);
            });
        }

        this.args.submit(this.valueObject);
    }

    @action
    updateUnit(e) {
        if (e.target.value) {
            set(this.valueObject, 'unit', e.target.value);
        }

        Object.entries(this.valueObject).forEach(([key, item]) => {
            set(this.args.valueObject, key, item);
        });

        this.args.submit(this.valueObject);
    }
}
