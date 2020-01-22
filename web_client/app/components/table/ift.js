import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class Ift extends Component {

    @tracked iftsArray;

    constructor() {
        super(...arguments);

        this.iftsArray = this.args.oil.ifts;
        
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
    updateInterface() {

    }

    @action
    updateTemperature() {
        
    }
}
