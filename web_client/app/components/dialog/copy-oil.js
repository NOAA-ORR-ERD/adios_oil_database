import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class CopyOilDlg extends Component {
    @tracked oilName;

    constructor() {
        super(...arguments);

        this.oilName = `Copy of ${this.args.oil.name}`;
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
    }

    @action
    submitForm() {
        let oil = this.args.oil.toJSON();

        oil.name = this.oilName;
        delete oil.id;

        this.args.submit(oil);
    }

}
