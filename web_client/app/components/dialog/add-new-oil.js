import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class AddNewOilDlg extends Component {
    @tracked name;

    get formFilledOut() {
        if (this.name) {
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
        $(element).on('shown.bs.modal', this.shown);
    }

    @action
    shown(event) {
        event.currentTarget.querySelector('input').focus();
    }

    @action
    updateName(event) {
        this.name = event.target.value;

        if (event.type === 'change' && this.formFilledOut) {
            this.okButton.focus();
        }
    }

    @action
    submitForm() {
        this.args.submit({
            name: this.name,
            samples: [{
                name: 'Fresh Oil Sample',
                short_name: 'Fresh Oil',
                fraction_weathered: 0
            }]
        });

    }

}
