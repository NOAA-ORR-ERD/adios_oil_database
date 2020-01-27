import Component from '@glimmer/component';
import { action } from "@ember/object";

export default class KinematicViscosity extends Component {
    @action
    submit(kvisValue) {
        this.args.oil.kvis = kvisValue;
        this.submit(this.args.oil);
    }
}
