import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import { roundRelative } from 'ember-oil-db/helpers/round-relative';

export default class AddSampleDlg extends Component {
    SampleTypes = {
        weathered: 0,
        distillate: 1,
        nameOnly: 2
    };

    @tracked sampleType = 0;

    @tracked weatheredFraction = NaN;
    @tracked distillateMin = NaN;
    @tracked distillateMax = NaN;
    @tracked sampleName;

    get formFilledOut() {
        switch (this.sampleType) {
        case this.SampleTypes.weathered:
            if (!Number.isNaN(this.weatheredFraction)) {
                return true;
            }
            break;
        case this.SampleTypes.distillate:
            if (!(Number.isNaN(this.distillateMin) &&
                  Number.isNaN(this.distillateMax))) {
                return true;
            }
            break;
        case this.SampleTypes.nameOnly:
            if (this.sampleName) {
                return true;
            }
            break;
        }

        return false;
    }

    @action
    updateFraction(event) {
        if (event.target.value === '') {
            this.weatheredFraction = NaN;
        }
        else {
            this.weatheredFraction = Number(event.target.value);
        }
    }

    @action
    updateDistillateMin(event) {
        if (event.target.value === '') {
            this.distillateMin = NaN;
        }
        else {
            this.distillateMin = Number(event.target.value);
        }
    }

    @action
    updateDistillateMax(event) {
        if (event.target.value === '') {
            this.distillateMax = NaN;
        }
        else {
            this.distillateMax = Number(event.target.value);
        }
    }

    @action
    updateName(event) {
        this.sampleName = event.target.value;
    }

    @action
    updateSampleType(choice) {
        this.sampleType = Number(choice.target.value);
    }

    @action
    submitForm() {
        let newSample;
        let name, shortName;
        let min, max;

        switch (this.sampleType) {
        case this.SampleTypes.weathered:
            if (this.weatheredFraction) {
                let percent = roundRelative([this.weatheredFraction * 100, 2]);
                name = shortName = `${percent}% Weathered`;
            }
            else {
                name = 'Fresh Oil Sample';
                shortName = 'Fresh Oil';
            }

            newSample = {
                'name': name,
                'short_name': shortName,
                'fraction_weathered': {
                    value: this.weatheredFraction * 100,
                    unit: '%'
                }
            };
            break;
        case this.SampleTypes.distillate:
            min = roundRelative([this.distillateMin, 2]);
            max = roundRelative([this.distillateMax, 2]);

            if (!(Number.isNaN(min) || Number.isNaN(max))) {
                name = shortName = `BP Range: [${min}\u2192${max}] °C`;
            }
            else if (Number.isNaN(min)) {
                name = shortName = `BP Range: <${max} °C`;
            }
            else {
                name = shortName = `BP Range: >${min} °C`;
            }

            newSample = {
                    'name': name,
                    'short_name': shortName,
                    'boiling_point_range': {
                        min_value: min,
                        max_value: max,
                        unit: 'C'
                    }
                };
            break;
        case this.SampleTypes.nameOnly:
            name = this.sampleName;

            if (name.length <= 12) {
                shortName = name;
            }
            else {
                shortName = `${name.substr(0, 12)}...`;
            }

            newSample = {
                    'name': name,
                    'short_name': shortName
                };
            break;
        }

        let oil = this.args.oil;
        oil.samples.pushObject(newSample);
        this.args.submit(oil);
    }

}
