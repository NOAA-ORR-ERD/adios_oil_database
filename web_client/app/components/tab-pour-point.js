import Component from '@ember/component';

import $ from 'jquery';

export default Component.extend({

    isShowingModal: false,
    isInterval: true,

    init(){
        this._super(...arguments);
        // TODO - initialize isInterval based on real data
        this.toggleInput();
    },
        
    toggleInput(){
        if(this.isInterval){
            $('#dialog-interval-input').prop('disabled', false);
            $('#dialog-value-input').prop('disabled', true);
        } else {
            $('#dialog-interval-input').prop('disabled', true);
            $('#dialog-value-input').prop('disabled', false);
        }
    },

    actions: {

        toggleModal(){
            this.toggleProperty('isShowingModal');
        },

        toggleRadio(){
            this.toggleProperty('isInterval');
        }
    }
});
