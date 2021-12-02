import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import $ from 'jquery';

const ESC_KEY = 27;


export default class MeasurementGroupsDialog extends Component {
    @tracked tempList;  // we use this until it is time to save, then use the base list.

    constructor() {
        super(...arguments);
        
        this.tempList = [...this.args.inputValue];

        this._initEscListener();
    }

    // add on ESC key event listener for dialog
    _initEscListener() {
        const closeOnEscapeKey = (ev) => {
            if (ev.keyCode === ESC_KEY) { 
                this.closeModal(); 
            }
        };   

        // Note: Ember doesn't want you to use JQuery for some purity reason,
        //       and it throws warnings when the app starts.
        //       But this is the recommended way to add an escape listener
        //       to an ember-modal-dialog according to their README.
        //
        //       https://github.com/yapplabs/ember-modal-dialog#keyboard-shortcuts
        $('body').on('keyup.modal-dialog', closeOnEscapeKey);  // eslint-disable-line ember/no-jquery
    }

    @action
    addNewGroup(index) {
        this.tempList.splice(index, 0, '');
        this.tempList = this.tempList;
    }

    @action
    deleteGroup(index) {
        this.tempList.splice(index, 1);
        this.tempList = this.tempList;
    }

    @action
    updateValue(enteredValue, index) {
        this.tempList[index] = enteredValue;
        this.tempList = this.tempList;
    }
    
    @action
    onSave(){
        this.args.inputValue.clear();
        this.tempList.map(i => {this.args.inputValue.push(i);});

        this.args.submit();
        this.closeModal();
    }

    @action
    closeModal() {
        this.args.closeModal();
    }
}
