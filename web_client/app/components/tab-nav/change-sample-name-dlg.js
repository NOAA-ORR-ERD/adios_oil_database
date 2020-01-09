import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class ChangeSampleNameDlg extends Component {
    @tracked sampleName;

    constructor() {
        super(...arguments);

        this.sampleName = this.args.oil.samples[this.args.index].short_name;
    }

    get formFilledOut() {
        if (this.sampleName) {
            return true;
        }

        return false;
    }

    @action
    updateName(event) {
        this.sampleName = event.target.value;
    }

    @action
    submitForm() {
        let name = this.sampleName;
        let shortName;

        if (name.length <= 12) {
            shortName = name;
        }
        else {
            shortName = `${name.substr(0, 12)}...`;
        }

        let oil = this.args.oil;
        oil.samples[this.args.index].short_name = shortName;
        this.args.submit(oil);
    }
}
