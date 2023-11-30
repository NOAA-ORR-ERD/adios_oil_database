import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import { service } from '@ember/service';


export default class BackToListButton extends Component {
    @service router;
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
