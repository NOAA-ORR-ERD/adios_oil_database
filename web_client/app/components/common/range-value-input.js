import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class RangeValueInput extends Component {

    @tracked isShowingModal = false;
    @tracked valueObject;
    @tracked inputValue;

    constructor() {
        super(...arguments);

        this.valueObject = this.args.valueObject;

        if(this.valueObject){
            this.inputValue = this.valueObject[this.args.valueName];
        }
        // form component ID - it needs to tether ember-modal-dialog to - replace spaces too
        this.componentId = this.args.valueTitle.replace(/\s+/g, '-').toLowerCase() + 
            this.args.sampleIndex;
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
        // TODO - do we need to keep properties other than value(s) and unit? (_cls, from_unit, etc.)

        if (enteredValue) {
            // check if all entered fields are not empty
            if (enteredValue.hasOwnProperty("min_value") ||
                enteredValue.hasOwnProperty("max_value") ||
                enteredValue.hasOwnProperty("value")) {

                if (this.valueObject) {
                    // there are source and enterd value(s) case
                    // min value
                    if(enteredValue.hasOwnProperty("min_value")){
                        this.valueObject[this.args.valueName].min_value = enteredValue.min_value;
                    } else {
                        if(this.valueObject[this.args.valueName].hasOwnProperty("min_value")) {
                            delete this.valueObject[this.args.valueName].min_value;
                        }
                    }
                    // max value
                    if (enteredValue.hasOwnProperty("max_value")) {
                        this.valueObject[this.args.valueName].max_value = enteredValue.max_value;
                    } else {
                        if(this.valueObject[this.args.valueName].hasOwnProperty("max_value")) {
                            delete this.valueObject[this.args.valueName].max_value
                        }
                    }
                    // scalar value
                    if (enteredValue.hasOwnProperty("value")) {
                        this.valueObject[this.args.valueName].value = enteredValue.value;
                    } else {
                        if(this.valueObject[this.args.valueName].hasOwnProperty("value")) {
                            delete this.valueObject[this.args.valueName].value
                        }
                    }
                    // save unit
                    this.valueObject[this.args.valueName].unit = enteredValue.unit;

                } else {
                    // there is enterd value but there is no source object - create one
                    this.valueObject = {
                        [this.args.valueName]: {
                            unit: enteredValue.unit
                        }
                    };

                    if (enteredValue.hasOwnProperty("value")) {
                        this.valueObject[this.args.valueName].value = enteredValue.value;
                    } else {
                        if (enteredValue.hasOwnProperty("min_value")) {
                            this.valueObject[this.args.valueName].min_value = enteredValue.min_value;
                        } 
                        if (enteredValue.hasOwnProperty("max_value")) {
                            this.valueObject[this.args.valueName].max_value = enteredValue.max_value;
                        } 
                    }
                }
            } else {
                // all entered fields are empty - remove source
                if (this.valueObject) {
                    this.valueObject = null;
                }
            }
        } else {
            // nothing entered - remove source 
            if (this.valueObject) {
                this.valueObject = null;
            }
        }    

        if (this.valueObject && this.valueObject[this.args.valueName]) {
            this.inputValue = this.valueObject[this.args.valueName];
        } else {
            this.inputValue = null;
        }
        this.valueObject = this.valueObject; // ember! - reset tracked object

        // TODO
        //this.args.updateValue(valueObject);
    }
}