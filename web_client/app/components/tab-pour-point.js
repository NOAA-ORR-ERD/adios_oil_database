import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class TabPourPoint extends Component {
    
    @tracked isShowingModal = false;

    constructor() {
        super(...arguments);

        if(this.args.oil){
            this.pour_point = this.args.oil.pour_point;
        }

        if(this.pour_point){
            if(Number.isFinite(this.pour_point.ref_temp.value)){
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
        }

        this.componentId = "pour_point" + this.args.sampleIndex;
    }
    
    get editable() {
        return this.args.editable;
    }

    get isThereInput() {
        // TODO
        return true;
    }

    @action
    openModalDialog(){
        this.isShowingModal = true;
        this.toggleInput();
    }

    @action
    closeModalDialog() {
        this.isShowingModal = false;
    }

    @action
    toggleRadio(){
        //this.toggleProperty('isInterval');
        this.toggleInput();
    }

    @action
    onSave(){
        alert("Saving");
        this.isShowingModal = false;
    }
}