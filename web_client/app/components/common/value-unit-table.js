import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class ValueUnitTable extends Component {

    @tracked valueArray = [];

    constructor() {
        super(...arguments);

        this.tableId = this.args.tableTitle.replace(/\s+/g, '-').toLowerCase();

        this.valueArray = this.args.valueArray;
        
        this.emptyRow = {
            [this.args.leftColumnValueName]: {
                value: NaN,
                unit: this.args.leftColumnUnit
            },
            [this.args.rightColumnValueName]: {
                value: NaN,
                unit: this.args.rightColumnUnit
            }
        };

    }

    @action
    deleteTableRow(event) {
        // find current table row
        let currentRow = event.currentTarget.parentNode.parentNode;
        // delete correspondent array item based on row index - table idex starts from 1
        this.valueArray.splice(currentRow.rowIndex - 1, 1);
        this.valueArray = this.valueArray; // !!! - to "reset" array for tracking

    }

    @action
    addEmptyTableRow(event) {

        if (this.valueArray ) {
            this.valueArray = [...this.valueArray, this.emptyRow];
        } else {
            this.valueArray = [this.emptyRow];
        }
        
    }

    @action
    updateLeftColumnValue(val) {
        // TODO
        {{debugger}}
    }

    @action
    updateRightColumnValue(val) {
        // TODO
    }

}