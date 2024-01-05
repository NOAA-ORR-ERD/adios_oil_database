import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";

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
    updateName(event) {
        this.oilName = event.target.value;

        if (['change', 'focusout'].includes(event.type) && this.formFilledOut) {
            this.okButton.focus();
        }
    }

    @action
    closeForm() {
        this.args.close();
    }

    @action
    submitForm() {
        let oil = this.args.oil.serialize().data.attributes;

        set(oil.metadata, 'name', this.oilName);
        delete oil.id;
        delete oil.oil_id;

        this.args.submit(oil);
    }

}
