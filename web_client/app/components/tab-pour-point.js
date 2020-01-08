import Component from '@ember/component';

import $ from 'jquery';

export default Component.extend({

    isShowingModal: false,
    isInterval: false,

    intervalMin: undefined,
    intervalMax: undefined,
    scalarValue: undefined,

    init(){
        {{debugger}}
        this._super(...arguments);
        let oil = this.get('oil');
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
        this.toggleInput();
    },
        
    toggleInput(){
        if(this.isInterval){
            $('#dialog-interval-input').prop('disabled', false);
            $('#dialog-scalar-input').prop('disabled', true);
        } else {
            $('#dialog-interval-input').prop('disabled', true);
            $('#dialog-scalar-input').prop('disabled', false);
        }
    },

    actions: {

        openModalDialog(){
            //$("#scalar-range-dialog").modal();
            this.set('isShowingModal', true);
            this.toggleInput();
        },

        closeModalDialog() {
            this.set('isShowingModal', false);
        },

        toggleRadio(){
            this.toggleProperty('isInterval');
            this.toggleInput();
        },
    
        onSave(){
            alert("Saving");
            //$("#scalar-range-dialog").hide();
        },

        onCancel(){
            alert("Closing");
            this.CloseModalDialog();
        }
    }
});
