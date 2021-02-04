import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";
import $ from 'jquery';

export default class CopyOilDlg extends Component {
    @tracked oilName;

    constructor() {
        super(...arguments);

        this.oilName = `Copy of ${this.args.oil.metadata.name}`;
    }

    get formFilledOut() {
        if (this.oilName) {
            return true;
        }

        return false;
    }

    @action
    setModalEvents(element) {
        // Note: Bootstrap modals can not be modified with event handlers until
        //       the elements are completely rendered.  So we can't add an 'on'
        //       handler in the template like you would normally be able to do.
        //       So we add a did-insert handler in the template, attaching it
        //       to this function.
        // Note: Ember doesn't want you to use JQuery for some purity reason,
        //       and it throws warnings when the app starts.
        //       Unfortunately, JQuery is the only way to add an event listener
        //       to a bootstrap modal.
        //       Don't believe me?  https://stackoverflow.com/questions/24211185/twitter-bootstrap-why-do-modal-events-work-in-jquery-but-not-in-pure-js
        $(element).on('shown.bs.modal', this.shown);  // eslint-disable-line ember/no-jquery
    }

    @action
    shown(event) {
        event.currentTarget.querySelector('input').focus();
    }

    @action
    updateName(event) {
        this.oilName = event.target.value;

        if (['change', 'focusout'].includes(event.type) && this.formFilledOut) {
            this.okButton.focus();
        }
    }

    @action
    submitForm() {
        let oil = this.args.oil.toJSON();

        set(oil.metadata, 'name', this.oilName);
        delete oil.id;

        this.args.submit(oil);
    }

}
