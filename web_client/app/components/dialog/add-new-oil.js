import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import { ref } from 'ember-ref-bucket';


export default class AddNewOilDlg extends Component {
    @tracked name;

    // @ref gives us a reference to a piece of our template
    @ref("okButton") okButton;

    get formFilledOut() {
        if (this.name) {
            return true;
        }

        return false;
    }

    @action
    updateName(event) {
        this.name = event.target.value;

        if (['change', 'focusout'].includes(event.type)
                && this.formFilledOut)
        {
            this.okButton.focus();
        }
    }

    @action
    closeForm() {
        this.args.close();
    }

    @action
    submitForm() {
        this.args.submit({
            metadata: {
                name: this.name
            },
            sub_samples: [{
                metadata: {
                    name: 'Fresh Oil Sample',
                    short_name: 'Fresh Oil',
                    fraction_evaporated: {
                        unit: '1',
                        unit_type: 'massfraction',
                        value: 0
                    }
                },
                physical_properties: {}
            }]
        });
    }
}
