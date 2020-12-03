import Component from '@glimmer/component';
import { action, set } from "@ember/object";


export default class SubsampleMetadata extends Component {
    @action
    updateDescription(event) {
        set(this.args.oil.metadata, 'description', event.target.value);
        this.args.submit(this.args.oil);
    }
}
