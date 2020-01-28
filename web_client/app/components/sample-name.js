import Component from '@glimmer/component';
import { action } from "@ember/object";
import { tracked } from '@glimmer/tracking';

export default class SampleName extends Component {
    @tracked name;

    @action
    submit() {
        let oil = this.args.oil;
        this.args.submit(oil);
    }
}
