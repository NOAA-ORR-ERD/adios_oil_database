import Component from '@glimmer/component';
import { action } from "@ember/object";

export default class Density extends Component {
    @action
    submit(dvisValue) {
        this.args.oil.dvis = dvisValue;
        this.args.submit(this.args.oil);
    }
}
