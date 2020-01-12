import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import { convertUnit } from 'ember-oil-db/helpers/convert-unit';
import { valueUnit } from 'ember-oil-db/helpers/value-unit';

export default class RangeValueDialog extends Component {
    
    @tracked isInterval = false;

    @tracked intervalMin = undefined;
    @tracked intervalMax = undefined;
    @tracked scalarValue = undefined;

    constructor() {
        super(...arguments);

        this.valueTitle = this.args.valueTitle;
        this.valueUnit = this.args.valueUnit;
        this.valuePrecision = this.args.valuePrecision;
        this.componentId = this.args.componentId;
        // create source and dialog value objects
        this.sourceValue = this.args.valueObject;

        // define if there is range
        if(Number.isFinite(this.sourceValue.value)){
            this.scalarValue = valueUnit([convertUnit([this.sourceValue, this.valueUnit]),
                this.valuePrecision, true]);
            this.isInterval = false;
        } else {
            // always select interval input if there is no scalar value (?)
            [this.intervalMin, this.intervalMax] = valueUnit([convertUnit(
                [this.sourceValue, this.valueUnit]), this.valuePrecision, true]);
            this.isInterval = true;
        }

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
        {{debugger}}
        this.isInterval = isRange;
   }

    @action
    closeModalDialog() {
        this.isShowingModal = false;
    }

    @action
    onSave(){
        alert("Saving");
        this.isShowingModal = false;
    }
}