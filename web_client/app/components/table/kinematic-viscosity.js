import Component from '@glimmer/component';
import { action, set } from "@ember/object";

export default class KinematicViscosity extends Component {
    @action
    submit(kvisValue) {
        set(this.args.oil, 'kvis', kvisValue);
        this.args.submit(this.args.oil);
    }
}
