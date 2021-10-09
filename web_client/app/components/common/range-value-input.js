import BaseComponent from './base-component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";


export default class RangeValueInput extends BaseComponent {
    @tracked isShowingModal = false;
    @tracked valueObject;
    @tracked inputValue;

    constructor() {
        super(...arguments);

        this.valueObject = this.args.valueObject;

        if(this.valueObject){
            this.inputValue = this.deepGet(this.valueObject, this.args.valueName);
        }
        // form component ID - it needs to tether ember-modal-dialog to - replace spaces too
        this.componentId = this.args.valueTitle.replace(/\s+/g, '-').toLowerCase() + 
            this.args.sampleIndex;
    }

    enteredValuesValid(entered) {
        if (!entered) { return false }

        if (!(entered.hasOwnProperty("min_value") ||
              entered.hasOwnProperty("max_value") ||
              entered.hasOwnProperty("value")))
        {
            return false;
        }

        return true;
    }

    get editable() {
        return this.args.editable;
    }

    @action
    openModalDialog(){
        this.isShowingModal = true;
    }

    @action
    closeModalDialog() {
        this.isShowingModal = false;
    }

    @action
    updateValue(enteredValue) {
        // enteredValue should be a mostly valid measurement object, but it is
        // missing a unit_type.  Let's see if a unit type was passed in.
        if (this.args.valueUnitType) {
            enteredValue.unit_type = this.args.valueUnitType;
        }

        if (this.enteredValuesValid(enteredValue)) {
            this.deepSet(this.valueObject, this.args.valueName, enteredValue);
            this.inputValue = enteredValue;
        }
        else {
            // nothing entered - This happens when we have no values in the
            // dialog and then press OK.  We will view this as an intentional
            // nullification of the property.
            this.deepRemove(this.valueObject, this.args.valueName);
            this.inputValue = null;
        }

        this.valueObject = this.valueObject; // ember! - reset tracked object

        if (this.args.submit) {
            this.args.submit();
        }
        else {
            console.warn('No submit method for', this.args.valueName);
        }
    }
}
