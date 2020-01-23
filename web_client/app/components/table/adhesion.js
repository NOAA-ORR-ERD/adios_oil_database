import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class Adhesion extends Component {
    @action
    submit() {
        this.args.submit(this.args.oil);
    }
}
