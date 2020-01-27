import Component from '@glimmer/component';
import { action } from "@ember/object";

export default class Distillation extends Component {
    @action
    submit(cutsValue) {
        this.args.oil.cuts = cutsValue;
        this.args.submit(this.args.oil);
    }
}
