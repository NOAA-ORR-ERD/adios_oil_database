import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import { valueUnitUnit } from 'ember-oil-db/helpers/value-unit-unit';
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

        this.numberStep = 1/Math.pow(10, this.args.valuePrecision);

        let unitObj = {"unit": this.args.valueUnit};
        this.beaUnit = valueUnitUnit([unitObj]);

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
        if(Number.isNaN(parseFloat(e.target.value))) {
            this.dialogValue = "";
        } else {
            this.dialogValue = parseFloat(e.target.value);
        }
        this.isThereInput = true;
    }

    @action
    changeMin(e) {
        if(Number.isNaN(parseFloat(e.target.value))) {
            this.dialogMinValue = "";
        } else {
            this.dialogMinValue = parseFloat(e.target.value);  
        }
        this.isThereInput = true;
    }

    @action
    changeMax(e){
        if(Number.isNaN(parseFloat(e.target.value))) {
            this.dialogMaxValue = "";
        } else {
            this.dialogMaxValue = parseFloat(e.target.value);
        }
        this.isThereInput = true;
    }

    @action
    onSave(){
        {{debugger}}
        let enteredValue = {"unit": this.args.valueUnit};
        
        if (this.isThereInput) {
            if (this.isInterval) {
                if (this.dialogMinValue !== "") {
                    enteredValue["min_value"] = this.dialogMinValue;
                }
                if (this.dialogMaxValue !== "") {
                    enteredValue["max_value"] = this.dialogMaxValue;
                }
            } else {
                if (this.dialogValue !== "") {
                    enteredValue["value"] = this.dialogValue;
                }
            }
            this.args.updateValue(enteredValue);
        }

        this.closeModalDialog() 
    }
}