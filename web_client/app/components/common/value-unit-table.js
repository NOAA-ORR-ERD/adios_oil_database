import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";

export default class ValueUnitTable extends Component {

    @tracked valueArray = [];

    constructor() {
        super(...arguments);

        this.tableId = this.args.tableTitle.replace(/\s+/g, '-').toLowerCase();
        this.valueArray = this.args.valueArray;
        
    }

    @action
    deleteTableRow(index) {
        // delete correspondent array item based on row index - table idex starts from 1
        this.valueArray.splice(index, 1);
        this.valueArray = this.valueArray; // !!! - to "reset" array for tracking

        this.updateValue(this.valueArray);
    }

    @action
    addEmptyTableRow(index) {

        if (!this.valueArray ) {
            this.valueArray = [];
        }

        this.valueArray.splice(index, 0, {});
        this.valueArray = this.valueArray;

        this.updateValue(this.valueArray);
    }

    @action
    updateCellValue(index, attrName, value) {
        set(this.valueArray[index], attrName, value);
        this.updateValue(this.valueArray);
    }

    @action
    updateValue(enteredValue) {
        this.args.submit(enteredValue);
    }
}