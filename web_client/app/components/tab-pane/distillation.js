import Component from '@glimmer/component';
import { action, set } from "@ember/object";
import { isBlank } from '@ember/utils';

export default class OilDemographics extends Component {
    constructor() {
        super(...arguments);
    }

    @action
    updateDistillationType(event) {
        let enteredType = event.target.value;

        if (isBlank(enteredType)) {
            delete this.args.oil.distillation_data.type;
        }
        else {
            set(this.args.oil.distillation_data, 'type', enteredType);
        }

        this.args.submit(this.args.oil);
    }

    @action
    updateDistillationMethod(event) {
        let enteredMethod = event.target.value;

        if (isBlank(enteredMethod)) {
            delete this.args.oil.distillation_data.method;
        }
        else {
            set(this.args.oil.distillation_data, 'method', enteredMethod);
        }

        this.args.submit(this.args.oil);
    }

    @action
    updateFractionRecovered(event) {
        let enteredFraction = event.target.value;

        if (isBlank(enteredFraction)) {
            delete this.args.oil.distillation_data.fraction_recovered;
        }
        else {
            set(this.args.oil.distillation_data, 'fraction_recovered',
                enteredFraction);
        }

        this.args.submit(this.args.oil);
    }

}
