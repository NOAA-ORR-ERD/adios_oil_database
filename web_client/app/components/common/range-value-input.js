import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class RangeValueInput extends Component {

    @tracked isShowingModal = false;
    @tracked valueObject;

    constructor() {
        super(...arguments);

        if(this.args.valueReference){
            this.valueObject = this.args.valueObject;
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
    updateValue(valueObject) {
        // TODO
        //this.args.updateValue(valueObject);
    }
}