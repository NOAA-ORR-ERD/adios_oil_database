import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class RangeValueDialog extends Component {
    
    @tracked isInterval = false;

    // @tracked intervalMin = undefined;
    // @tracked intervalMax = undefined;
    // @tracked scalarValue = undefined;

    constructor() {
        super(...arguments);

        let args = [...arguments];

        {{debugger}}

        if(Number.isFinite(this.args.valueObject.value)){
            //this.scalarValue = this.pour_point.ref_temp.value;
            this.isInterval = false;
        } else {
            // always select interval input if there is no scalar value
            this.isInterval = true;
        }
            // if(this.pour_point.ref_temp.min_value){
            //     //this.intervalMin = this.pour_point.ref_temp.min_value;
            // }
            // if(this.pour_point.ref_temp.max_value){
            //     //this.intervalMax = this.pour_point.ref_temp.max_value;
            //     this.isInterval = true;
            // }

        this.valueObject = this.args.ValueObject; 
        this.valueTitle = this.args.valueTitle;
        this.valueUnit = this.args.valueUnit;
        this.componentId = this.valueTitle + this.args.sampleIndex;
    }
    
    get isThereInput() {
        // TODO
        return true;
    }

    toggleInput(){
        // if(this.isInterval){
        //     $('#dialog-interval-input').prop('disabled', false);
        //     $('#dialog-scalar-input').prop('disabled', true);
        // } else {
        //     $('#dialog-interval-input').prop('disabled', true);
        //     $('#dialog-scalar-input').prop('disabled', false);
        // }
    }

    @action
    toggleRadio(){
        //this.toggleProperty('isInterval');
        this.toggleInput();
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