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
        if(Array.isArray(this.valueArray)) {
            let i = this.valueArray.length;

            while(i--) {
                if (this.valueArray[i][this.args.leftColumnValueName] &&
                    this.valueArray[i][this.args.rightColumnValueName]) {
                    if (Number.isNaN(parseFloat(this.valueArray[i][this.args.leftColumnValueName].value)) &&
                        Number.isNaN(parseFloat(this.valueArray[i][this.args.rightColumnValueName].value))) {
                            this.valueArray.splice(i, 1);
                    }
                }
            }
            this.valueArray = [...this.valueArray];
        }
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
        if(valueObject) {
            if(Number.isNaN(parseFloat(valueObject.value))){
                // value has been removed (emty field) or is NaN
                if(this.valueArray[index][this.args.leftColumnValueName]){
                    this.valueArray[index][this.args.leftColumnValueName].value = NaN;
                }   // do nothing if valueArray[index] has no leftColumnValueName property
            } else {    // not NaN value
                if(this.valueArray[index][this.args.leftColumnValueName]){
                    this.valueArray[index][this.args.leftColumnValueName].value = valueObject.value;
                    this.valueArray[index][this.args.leftColumnValueName].unit = valueObject.unit;
                } else { // there is no value object in valueArray
                    this.valueArray[index] = {
                        [this.args.leftColumnValueName]: {
                            value: valueObject.value, 
                            unit: valueObject.unit
                        }
                    };
                }
            }
        } else {    // null, etc. - value has been removed (emty field)
            if(this.valueArray[index][this.args.leftColumnValueName]){
                this.valueArray[index][this.args.leftColumnValueName].value = NaN; 
            }
        }

        this.removeEmptyTableRows();
    }

    @action
    updateRightColumnValue(index, valueObject) {
        if(valueObject) {
            if(Number.isNaN(parseFloat(valueObject.value))){
                // value has been removed (emty field) or is NaN
                if(this.valueArray[index][this.args.rightColumnValueName]){
                    this.valueArray[index][this.args.rightColumnValueName].value = NaN;
                }   // do nothing if valueArray[index] has no 'rightColumnValueName' property
            } else {    // not NaN value
                if(this.valueArray[index][this.args.rightColumnValueName]){
                    this.valueArray[index][this.args.rightColumnValueName].value = valueObject.value;
                    this.valueArray[index][this.args.rightColumnValueName].unit = valueObject.unit;
                } else { // there is no value object in valueArray
                    this.valueArray[index] = {
                        [this.args.rightColumnValueName]: {
                            value: valueObject.value, 
                            unit: valueObject.unit
                        }
                    };
                }
            }
        } else {    // null, etc. - value has been removed (emty field)
            if(this.valueArray[index][this.args.rightColumnValueName]){
                this.valueArray[index][this.args.rightColumnValueName].value = NaN; 
            }
        }

        this.removeEmptyTableRows();
    }
}