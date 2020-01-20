import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class RangeValueInput extends Component {

    @tracked isShowingModal = false;
    @tracked valueObject;
    
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
        if(this.valueObject) {
            if(enteredValue) {
                // there are source and enterd value(s) case
                // min value
                if(enteredValue.min_value){
                    this.valueObject[this.args.valueName].min_value = enteredValue.min_value;
                } else {
                    if(this.valueObject[this.args.valueName].min_value) {
                        delete this.valueObject[this.args.valueName].min_value
                    }
                }
                // max value
                if(enteredValue.max_value){
                    this.valueObject[this.args.valueName].max_value = enteredValue.max_value;
                } else {
                    if(this.valueObject[this.args.valueName].max_value) {
                        delete this.valueObject[this.args.valueName].max_value
                    }
                }
                // scalar value
                if(enteredValue.value){
                    this.valueObject[this.args.valueName].value = enteredValue.value;
                } else {
                    if(this.valueObject[this.args.valueName].value) {
                        delete this.valueObject[this.args.valueName].value
                    }
                }
                // save unit
                this.valueObject[this.args.valueName].unit = enteredValue.unit;

            } else if(this.valueObject[this.args.valueName]) {
                // there is source value but tere is no entered value - remove from source
                delete this.valueObject[this.args.valueName];
            }   // else do nothing - there are no source and entered value

        } else {
            if(enteredValue) {
                // there is enterd value but there is no source object - create one
                this.valueObject = {
                    [this.args.valueName]: enteredValue
                }
            }   // else do nothing - there are no source object and entered value(s)
        }

            //  // check if all fields are not empty
            //  if(this.valueObject.value || this.valueObject.min_value || this.valueObject.max_value) {
            //     this.valueObject.unit = valueObject.unit;
            //     this.valueObject = this.valueObject; // ember! - reset tracked object
            // } else {    // all fields are empty - remove object (?)
            //     this.valueObject = null;
            // }

        // TODO
        //this.args.updateValue(valueObject);
    }
}