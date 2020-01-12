import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import { convertUnit } from 'ember-oil-db/helpers/convert-unit';
import { valueUnit } from 'ember-oil-db/helpers/value-unit';

export default class RangeValueDialog extends Component {
    
    @tracked isInterval = false;

    constructor() {
        super(...arguments);

        this.valueTitle = this.args.valueTitle;
        this.valueUnit = this.args.valueUnit;
        this.valuePrecision = this.args.valuePrecision;
        this.componentId = this.args.componentId;
        // create source and dialog value objects
        this.sourceValue = this.args.valueObject;
        this.dialogValue = {};
        this.dialogValue["unit"] = this.valueUnit;

        // define if there is range
        if(Number.isFinite(this.sourceValue.value)){
            this.dialogValue["value"] = valueUnit([convertUnit([this.sourceValue, this.valueUnit]),
                this.valuePrecision, true]);
            this.isInterval = false;
        } else {
            // always select interval input if there is no scalar value (?)
            let valMin, valMax;
            [valMin, valMax] = valueUnit([convertUnit(
                [this.sourceValue, this.valueUnit]), this.valuePrecision, true]);
            this.dialogValue["min"] = valMin;
            this.dialogValue["max"] = valMax;
            this.isInterval = true;
        }

        this.isShowingModal = true;
    }
    
    get argNames() {
        return Object.keys(this.args);
    }

    get isThereInput() {
        // TODO
        return true;
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
        this.dialogValue["value"] = Number(e.target.value);
    }

    @action
    changeMin(e) {
        this.dialogValue["min"] = Number(e.target.value);
    }

    @action
    changeMax(e){
        this.dialogValue["max"] = Number(e.target.value);
    }

    @action
    onSave(){

        {{debugger}}
        
        if (this.isThereInput) {
            // prepare value object for back conversion
            if (this.isInterval) {
                delete this.dialogValue.value;
            } else {
                delete this.dialogValue.min;
                delete this.dialogValue.max;
            }

            // convert to source units
            let targetValue = convertUnit([this.dialogValue, this.sourceValue.unit]);
            // update parent value object
            this.args.updateValue(targetValue);
        
        }
        this.closeModalDialog() 
    }
}