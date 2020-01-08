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
        case this.SampleTypes.distillate:
            if (!(Number.isNaN(this.distillateMin) &&
                  Number.isNaN(this.distillateMax))) {
                return true;
            }
        case this.SampleTypes.nameOnly:
            if (this.sampleName) {
                return true;
            }
        }
        
        return false;
    }

    @action
    updateFraction(event) {
        this.weatheredFraction = Number(event.target.value);
    }

    @action
    updateDistillateMin(event) {
        this.distillateMin = Number(event.target.value);
    }

    @action
    updateDistillateMax(event) {
        this.distillateMax = Number(event.target.value);
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
        console.log('add-sample: submitForm()...');
        let newSample;
        let name, shortName;

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
                'fraction_weathered': this.weatheredFraction
            };
            break;
        case this.SampleTypes.distillate:
            let min = roundRelative([this.distillateMin, 2]);
            let max = roundRelative([this.distillateMax, 2]);

            name = shortName = `BP Range: ${min} &deg;F -> ${max} &deg;F`;

            newSample = {
                    'name': name,
                    'short_name': shortName,
                    'boiling_point_range': [min, max]
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

        console.log('newSample = ', newSample);

    }

};
