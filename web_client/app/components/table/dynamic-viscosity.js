import Component from '@glimmer/component';
import { action, set } from "@ember/object";

export default class Density extends Component {
    @action
    submit(dvisValue) {
        set(this.args.oil, 'dvis', dvisValue);
        this.args.submit(this.args.oil);
    }
}
