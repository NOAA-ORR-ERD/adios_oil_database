import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import { valueUnitUnit } from 'ember-oil-db/helpers/value-unit-unit';
import { convertUnit } from 'ember-oil-db/helpers/convert-unit';
import { valueUnit } from 'ember-oil-db/helpers/value-unit';
import $ from 'jquery';

const ESC_KEY = 27;

export default class RangeValueDialog extends Component {
    
    @tracked isInterval = false;

    @tracked dialogValue = "";
    @tracked dialogMinValue = "";
    @tracked dialogMaxValue = "";

    constructor() {
        super(...arguments);
        this._initEscListener();

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

    // add on ESC key event listener for dialog
    _initEscListener() {
        const closeOnEscapeKey = (ev) => {
            if (ev.keyCode === ESC_KEY) { 
                this.closeModalDialog(); 
            }
        };   
        $('body').on('keyup.modal-dialog', closeOnEscapeKey);
    }

    willDestroy() {
        $('body').off('keyup.modal-dialog');
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
    }

    @action
    changeMin(e) {
        if(Number.isNaN(parseFloat(e.target.value))) {
            this.dialogMinValue = "";
        } else {
            this.dialogMinValue = parseFloat(e.target.value);  
        }
    }

    @action
    changeMax(e){
        if(Number.isNaN(parseFloat(e.target.value))) {
            this.dialogMaxValue = "";
        } else {
            this.dialogMaxValue = parseFloat(e.target.value);
        }
    }

    @action
    onSave(){
        let closeDialog = true;

        // check if input fileds are empty
        if (!this.isInterval && this.dialogValue === "" ||
            this.isInterval && this.dialogMinValue === "" &&
            this.dialogMaxValue === "")
        {

            let confirmMessage = "The input has no numeric value(s). If you save it " +
                this.args.valueTitle + " property will have no data in this oil record."
            if (!confirm(confirmMessage)) {
                closeDialog = false;
            }
        }

        if (closeDialog) {
            let enteredValue = {"unit": this.args.valueUnit};
        
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

            this.closeModalDialog();
        }
    }
}