import Component from '@glimmer/component';
import { action, set } from "@ember/object";

export default class Distillation extends Component {
    @action
    submit(cutsValue) {
        set(this.args.oil.distillation_data, 'cuts', cutsValue);
        this.args.submit(this.args.oil);
    }
}
