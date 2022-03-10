import Component from '@glimmer/component';
import { action } from "@ember/object";
import { inject as service } from '@ember/service';


export default class BackToListButton extends Component {
    @service router;

    @action
    submit() {
        this.args.submit(this.args.oil);
    }

}
