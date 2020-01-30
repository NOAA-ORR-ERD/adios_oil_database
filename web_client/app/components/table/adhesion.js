import Component from '@glimmer/component';
import { action } from "@ember/object";

export default class Adhesion extends Component {
    @action
    submit() {
        this.args.submit(this.args.oil);
    }
}
