import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class Ift extends Component {

    @tracked iftsArray;
    // TODO - process updates like deepGet/deepSet from range-value-input
    // but do not return null - remove correspondent subobject instead
    @tracked interface;

    constructor() {
        super(...arguments);

        this.iftsArray = this.args.oil.ifts;
        if(Array.isArray(this.iftsArray)) {
            this.interface = this.iftsArray.map(function(x) { return x.interface; });
        } else {
            this.interface = [];
        }
    }

    @action
    deleteTableRow(e) {
        // find current table row
        let currentRow = e.currentTarget.parentNode.parentNode;
        // delete correspondent array item based on row index - table idex starts from 1
        this.iftsArray.splice(currentRow.rowIndex - 1, 1);
        this.iftsArray = this.iftsArray; // !!! - to "reset" array for tracking
    }

    @action
    addEmptyTableRow() {

        if (!this.iftsArray ) {
            this.iftsArray = [];
        }
        this.iftsArray.push({
            Tension: {
                value: NaN,
                unit: "N/m"
            },
            Temperature: {
                value: NaN,
                unit: "C"
            }
        });

        this.iftsArray = this.iftsArray;
    }

    @action
    updateInterface(index, e) {
        this.interface[index] = e.target.value;
        this.submit();
    }

    @action
    updateTension(valueObject) {
        // TODO
        //
        // a) valueObject is null
        // b) valueObject is {value: x, unit: "yyy"}
        //
        // also initial value state:
        //   1. iftsArray is null
        //   2. iftsArray[index].tension is null
        //   3. iftsArray[index].tension is {value: x, unit: "yyy"}
        
        // this.submit();

    }

    @action
    updateTemperature(valueObject) {
        // TODO
        //
        // a) valueObject is null
        // b) valueObject is {value: x, unit: "yyy"}
        //
        // also initial value state:
        //   1. iftsArray is null
        //   2. iftsArray[index].ref_temp is null
        //   3. iftsArray[index].ref_temp is {value: x, unit: "yyy"}

        //this.submit();
    }

    @action submit() {
        // TODO
        //this.args.submit(this.iftsArray);
    }
}
