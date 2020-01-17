import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class ValueUnitTable extends Component {

    @tracked valueArray = [];

    constructor() {
        super(...arguments);

        this.tableId = this.args.tableTitle.replace(/\s+/g, '-').toLowerCase();

        this.valueArray = this.args.valueArray;
    }

    @action
    deleteTableRow(event) {
        // find current table row
        let currentRow = event.currentTarget.parentNode.parentNode;
        // dlete table row
        currentRow.parentNode.removeChild(currentRow);
        // delete correspondent array item based on row index - table idex starts from 1
        delete this.valueArray[currentRow.rowIndex-1];
    }

    @action
    addTableRow() {

    }

    @action
    updateValue() {
        // TODO
    }
    
}