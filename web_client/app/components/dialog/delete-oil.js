import Component from '@glimmer/component';
import { action } from "@ember/object";

export default class DeleteOilDlg extends Component {
    @action
    closeForm() {
        this.args.close();
    }

    @action
    submitForm() {
        this.args.submit(this.args.oil);
    }

}
