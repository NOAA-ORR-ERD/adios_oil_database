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
        // Unfortunately, this is the only way to bind handlers to a bootstrap
        // modal.  You need to show the modal first.
        $(element).modal('show').on('shown.bs.modal', this.shown);
        $(element).modal('hide');
    }

    @action
    shown(event) {
        event.currentTarget.querySelector('input').focus();
    }

    @action
    updateName(event) {
        this.name = event.target.value;
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
