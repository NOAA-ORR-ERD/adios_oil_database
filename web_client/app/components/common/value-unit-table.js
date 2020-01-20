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

    removeEmptyTableRows() {
        // TODO
    }

    @action
    deleteTableRow(e) {
        // find current table row
        let currentRow = e.currentTarget.parentNode.parentNode;
        // delete correspondent array item based on row index - table idex starts from 1
        this.valueArray.splice(currentRow.rowIndex - 1, 1);
        this.valueArray = this.valueArray; // !!! - to "reset" array for tracking

    }

    @action
    addEmptyTableRow() {

        if (!this.valueArray ) {
            this.valueArray = [];
        }
        this.valueArray.push({
            [this.args.leftColumnValueName]: {
                value: NaN,
                unit: this.args.leftColumnUnit
            },
            [this.args.rightColumnValueName]: {
                value: NaN,
                unit: this.args.rightColumnUnit
            }
        });

        this.valueArray = this.valueArray;
    }

    @action
    updateLeftColumnValue(index, valueObject) {
        // TODO
        // if(valueObject) {
        //     if(Number.isNaN(valueObject.value)){
        //         if(this.valueArray[index][this.args.leftColumnValueName]){
        //             this.valueArray[index][this.args.leftColumnValueName].value = NaN;
        //         }
        //     } else {
        //         if(this.valueArray[index][this.args.leftColumnValueName]){
        //             this.valueArray[index][this.args.leftColumnValueName].value = valueObject.value;
        //     }
        // }
    }

    @action
    updateRightColumnValue(index, valueObject) {
        // TODO
    }

}