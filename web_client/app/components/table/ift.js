import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";

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
    deleteTableRow(index) {
        this.iftsArray.splice(index, 1);
        this.iftsArray = this.iftsArray; // !!! - to "reset" array for tracking

        this.updateTable(this.iftsArray);
    }

    @action
    addEmptyTableRow(index) {
        if (!this.iftsArray ) {
            this.iftsArray = [];
        }

        this.iftsArray.splice(index, 0, {});
        this.iftsArray = this.iftsArray;

        this.updateTable(this.iftsArray);
    }

    @action
    updateInterface(index, e) {
        if (e.target.value === '') {
            // empty value chosen, delete the property if it exists
            if (this.iftsArray[index].hasOwnProperty('interface')) {
                delete this.iftsArray[index].interface;
            }
        }
        else {
            set(this.iftsArray[index], 'interface', e.target.value);
        }

        this.updateTable(this.iftsArray);
    }

    @action
    updateAttr(index, attrName, value) {
        if (value) {
            set(this.iftsArray[index], attrName, value);
        }
        else {
            // empty value chosen, delete the property if it exists
            if (this.iftsArray[index].hasOwnProperty(attrName)) {
                delete this.iftsArray[index][attrName];
            }
        }

        this.updateTable(this.iftsArray);
    }

    @action
    updateTable(enteredValue) {
        this.args.submit(enteredValue);
    }

}
