import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";


export default class SaveEditsButton extends Component {
    @tracked dialogVisible = false;

    @action
    show_dialog(event) {
        this.dialogVisible = true;
    }

    @action
    close_dialog(event) {
        this.dialogVisible = false;
    }

    @action
    submit() {
        this.args.submit(this.args.oil);
    }

}
