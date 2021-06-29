import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";
import { isBlank } from '@ember/utils';

export default class OilDemographics extends Component {
    @tracked distillationType;

    constructor() {
        super(...arguments);
        
        this.distillationType = (this.args.oil.distillation_data || {}).type || 'unknown';
    }

    @action
    updateDistillationType(event) {
        let enteredType = event.target.value === 'unknown' ? null : event.target.value;

        if (isBlank(enteredType)) {
            delete this.args.oil.distillation_data.type;
        }
        else {
            if (!this.args.oil.distillation_data) {
                set(this.args.oil, 'distillation_data', {});
            }

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
            if (!this.args.oil.distillation_data) {
                set(this.args.oil, 'distillation_data', {});
            }

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
            if (!this.args.oil.distillation_data) {
                set(this.args.oil, 'distillation_data', {});
            }

            set(this.args.oil.distillation_data, 'fraction_recovered',
                enteredFraction);
        }

        this.args.submit(this.args.oil);
    }

}
