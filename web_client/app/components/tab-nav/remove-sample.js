import Component from '@glimmer/component';
import { action } from "@ember/object";

export default class RemoveSample extends Component {
    @action
    removeSample(sampleIndex) {
        // remove the sample
        let oil = this.args.oil;
        oil.sub_samples.removeAt(sampleIndex, 1);

        this.args.submit(oil);
    }
}
