import Component from '@glimmer/component';
import { action, set } from "@ember/object";

export default class Distillation extends Component {
    @action
    submit(cutsValue) {
        // prune any empty distillation cut attributes because they will cause
        // problems with the api server validation
        cutsValue.forEach(cut => {
            ['fraction','vapor_temp'].forEach(label => {
                if (cut.hasOwnProperty(label) && Object.keys(cut[label]).length === 0) {
                    delete cut[label]
                }
            });
        });

        set(this.args.oil.distillation_data, 'cuts', cutsValue);
        this.args.submit(this.args.oil);
    }
}
