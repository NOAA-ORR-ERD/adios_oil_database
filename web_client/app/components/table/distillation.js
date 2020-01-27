import Component from '@glimmer/component';
import { action, set } from "@ember/object";

export default class Distillation extends Component {
    @action
    submit(cutsValue) {
        set(this.args.oil, 'cuts', cutsValue);
        this.args.submit(this.args.oil);
    }
}
