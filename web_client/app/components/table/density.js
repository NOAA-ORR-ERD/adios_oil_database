import Component from '@glimmer/component';
import { action } from "@ember/object";

export default class Density extends Component {
    @action
    submit(densitiesValue) {
        this.args.oil.densities = densitiesValue;
        this.args.submit(this.args.oil);
    }
}
