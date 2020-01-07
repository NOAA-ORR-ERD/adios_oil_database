import Component from '@ember/component';

import $ from 'jquery';

export default Component.extend({

    isShowingModal: false,
    isInterval: false,

    intervalMin: undefined,
    intervalMax: undefined,
    scalarValue: undefined,

    init(){
        this._super(...arguments);
        let oil = this.get('oil');
        if(oil.pour_point){
            if(oil.pour_point.value){
                this.scalarValue = oil.pour_point.value;
                this.isInterval = false;
            }
            if(oil.pour_point.min_value){
                this.scalarValue = oil.pour_point.min_value;
                this.isInterval = true;
            }
            if(oil.pour_point.max_value){
                this.scalarValue = oil.pour_point.max_value;
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

        toggleModal(){
            this.toggleProperty('isShowingModal');
            if(this.isShowingModal)
            {
                this.toggleInput();
            }
        },

        toggleRadio(){
            this.toggleProperty('isInterval');
            this.toggleInput();
        },

        getModalInput(){
            alert("!!!");
        }
    }
});
