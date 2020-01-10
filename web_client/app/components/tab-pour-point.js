import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class TabPourPoint extends Component {

    @tracked isShowingModal = false;
    @tracked isInterval = false;

    @tracked intervalMin = undefined;
    @tracked intervalMax = undefined;
    @tracked scalarValue = undefined;

    constructor() {
        super(...arguments);

        {{debugger}}

        let oil = this.args.oil;
        if(oil.pour_point){
            if(oil.pour_point.ref_temp.value){
                this.scalarValue = oil.pour_point.ref_temp.value;
                this.isInterval = false;
            }
            if(oil.pour_point.ref_temp.min_value){
                this.scalarValue = oil.pour_point.ref_temp.min_value;
                this.isInterval = true;
            }
            if(oil.pour_point.ref_temp.max_value){
                this.scalarValue = oil.pour_point.ref_temp.max_value;
                this.isInterval = true;
            }
        }

}
    
    // init(){
    //     {{debugger}}
    //     this._super(...arguments);
    //     let oil = this.get('oil');
    //     if(oil.pour_point){
    //         if(oil.pour_point.ref_temp.value){
    //             this.scalarValue = oil.pour_point.ref_temp.value;
    //             this.isInterval = false;
    //         }
    //         if(oil.pour_point.ref_temp.min_value){
    //             this.scalarValue = oil.pour_point.ref_temp.min_value;
    //             this.isInterval = true;
    //         }
    //         if(oil.pour_point.ref_temp.max_value){
    //             this.scalarValue = oil.pour_point.ref_temp.max_value;
    //             this.isInterval = true;
    //         }
    //     }
    //     this.toggleInput();
    //}
    
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
    }
}
