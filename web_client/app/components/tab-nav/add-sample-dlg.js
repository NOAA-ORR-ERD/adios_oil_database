import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import { roundRelative } from 'adios-db/helpers/round-relative';
import $ from 'jquery';

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
    setModalEvents(element) {
        // Note: Bootstrap modals can not be modified with event handlers until
        //       the elements are completely rendered.  So we can't add an 'on'
        //       handler in the template like you would normally be able to do.
        //       So we add a did-insert handler in the template, attaching it
        //       to this function.
        // Note: Ember doesn't want you to use JQuery for some purity reason,
        //       and it throws warnings when the app starts.
        //       Unfortunately, JQuery is the only way to add an event listener
        //       to a bootstrap modal.
        //       Don't believe me?  https://stackoverflow.com/questions/24211185/twitter-bootstrap-why-do-modal-events-work-in-jquery-but-not-in-pure-js
        $(element).on('shown.bs.modal', this.shown);  // eslint-disable-line ember/no-jquery
    }

    @action
    shown(event) {
        event.currentTarget.querySelector('input').focus();
    }

    @action
    updateFraction(event) {
        if (event.target.value === '') {
            this.weatheredFraction = NaN;
        }
        else {
            this.weatheredFraction = Number(event.target.value);
        }

        if (['change', 'focusout'].includes(event.type) && this.formFilledOut) {
            this.okButton.focus();
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

        if (['change', 'focusout'].includes(event.type) && this.formFilledOut) {
            this.okButton.focus();
        }
    }

    @action
    updateName(event) {
        this.sampleName = event.target.value;

        if (['change', 'focusout'].includes(event.type) && this.formFilledOut) {
            this.okButton.focus();
        }
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
        let unit;

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
                'metadata': {
                    'name': name,
                    'short_name': shortName,
                    'fraction_weathered': this.weatheredFraction
                }
            };
            break;
        case this.SampleTypes.distillate:
            min = roundRelative([this.distillateMin, 2]);
            max = roundRelative([this.distillateMax, 2]);
            unit = 'C';


            if (!(Number.isNaN(min) || Number.isNaN(max))) {
                name = shortName = `BP Range: ${min} °${unit} \u2192 ${max} °${unit}`;
            }
            else if (Number.isNaN(min)) {
                name = shortName = `BP Range: <${max} °${unit}`;
            }
            else {
                name = shortName = `BP Range: >${min} °${unit}`;
            }

            newSample = {
                'metadata': {
                    'name': name,
                    'short_name': shortName,
                    'boiling_point_range': {
                        'unit': unit,
                        'min_value': min,
                        'max_value': max
                    }
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
                'metadata': {
                    'name': name,
                    'short_name': shortName
                }
            };
            break;
        }

        let oil = this.args.oil;
        oil.sub_samples.pushObject(newSample);
        this.args.submit(oil);
    }

}
