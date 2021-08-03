import Component from '@glimmer/component';
import { action, set } from "@ember/object";

export default class Density extends Component {
    @action
    submit(densitiesValue) {
        set(this.args.oil.physical_properties, 'densities', densitiesValue);
        this.args.submit(this.args.oil);
    }
}
