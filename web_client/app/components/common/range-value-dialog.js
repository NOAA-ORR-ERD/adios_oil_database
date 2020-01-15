import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import { convertUnit } from 'ember-oil-db/helpers/convert-unit';
import { valueUnit } from 'ember-oil-db/helpers/value-unit';

export default class RangeValueDialog extends Component {
    
    @tracked isInterval = false;

    @tracked dialogValue = "";
    @tracked dialogMinValue = "";
    @tracked dialogMaxValue = "";

    isThereInput = false;

    constructor() {
        super(...arguments);

        //this.valueTitle = this.args.valueTitle;
        this.componentId = this.args.componentId;
        this.sourceValue = this.args.valueObject;

        if(this.sourceValue)
        {
            // check if there is a range value
            if(Number.isFinite(this.sourceValue.value)){
                this.dialogValue = valueUnit([convertUnit([this.sourceValue, this.args.valueUnit]),
                this.args.valuePrecision, true]);
                this.isInterval = false;
            } else {
                // always select interval input if there is no scalar value (?)
                let valMin, valMax;
                [valMin, valMax] = valueUnit([convertUnit(
                    [this.sourceValue, this.args.valueUnit]), this.args.valuePrecision, true]);
                this.dialogMinValue = valMin;
                this.dialogMaxValue = valMax;
                this.isInterval = true;
            }
        } else {
            this.dialogValue = "";
        }
        this.isShowingModal = true;
    }
    
    get argNames() {
        return Object.keys(this.args);
    }

    get isThereInput() {
        return this.isThereInput;
    }

    // set isThereInput(state) {
    //     this.isThereInput = state;
    // }

    @action
    toggleRadio(isRange){
        this.isInterval = isRange;
   }

    @action
    closeModalDialog() {
        this.args.closeModalDialog();
    }

    @action
    changeValue(e) {
        if(isNaN(e.target.value)) {
            this.dialogValue = "";
        } else {
            this.dialogValue = Number(e.target.value);
        }
        this.isThereInput = true;
    }

    @action
    changeMin(e) {
        if(isNaN(e.target.value)) {
            this.dialogMinValue = "";
        } else {
            this.dialogMinValue = Number(e.target.value);  
        }
        this.isThereInput = true;
    }

    @action
    changeMax(e){
        if(isNaN(e.target.value)) {
            this.dialogMaxValue = "";
        } else {
            this.dialogMaxValue = Number(e.target.value);
        }
        this.isThereInput = true;
    }

    @action
    onSave(){
        var closeDialog = false;
        let enteredValue = {"unit": this.args.valueUnit};
        
        if (this.isThereInput) {
            // prepare value object for back conversion
            if (this.isInterval) {
                if (this.dialogMinValue) {
                    enteredValue["min_value"] = this.dialogMinValue;
                    closeDialog = true;
                }
                if (this.dialogMaxValue) {
                    enteredValue["max_value"] = this.dialogMaxValue;
                    closeDialog = true;
                }
            } else {
                // it must be not empty
                if (this.dialogValue) {
                    enteredValue["value"] = this.dialogValue;
                    closeDialog = true;
                } else {
                    alert ("Entered value is empty");
                    // do not close dialog ?
                }
            
            }
            // TODO - update parent value object 
            //this.args.updateValue(enteredValue);
        } else {
            // nothing has been changed - do not close dialog?
            alert ("Nothing has been changed or entered!");
        }

        if (closeDialog) {
            this.closeModalDialog() 
        }
    }
}