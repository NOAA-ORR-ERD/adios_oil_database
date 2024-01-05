import BaseComponent from '../common/base-component';
import { action } from "@ember/object";


export default class LogChangesDlg extends BaseComponent {
    @action
    closeForm() {
        this.args.close();
    }

    @action
    submitForm() {
        this.args.submit(this.args.oil);
    }
}
