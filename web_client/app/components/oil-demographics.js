import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";
import moment from 'moment';
import { isBlank } from '@ember/utils';

export default class OilDemographics extends Component {
    @tracked selectedLabels;
    @tracked filteredLabels;

    constructor() {
        super(...arguments);

        this.selectedLabels = this.args.oil.metadata.labels;
        this.filteredLabels = this.getFilteredLabels(
            this.args.oil.metadata.product_type
        );
    }

    getFilteredLabels(productType) {
        if (productType) {
            return this.args.labels.filter(i => {
                return i.product_types.includes(productType);
            }).mapBy('name');
        }
        else {
            return this.args.labels.mapBy('name');
        }
    }

    @action
    updateAPI(event) {
        let enteredAPI = event.target.value;

        if (isBlank(enteredAPI)) {
            delete this.args.oil.metadata.API;
        }
        else {
            set(this.args.oil.metadata, 'API', Number(enteredAPI));
        }

        this.args.submit(this.args.oil);
    }

    @action
    updateLocation(event) {
        set(this.args.oil.metadata, 'location', event.target.value);
        this.args.submit(this.args.oil);
    }

    @action
    updateType(event) {
        set(this.args.oil.metadata, 'product_type', event.target.value);

        this.filteredLabels = this.getFilteredLabels(
                this.args.oil.metadata.product_type
        );

        this.args.submit(this.args.oil);
    }

    @action
    updateLabels(selectedLabels) {
        this.selectedLabels = selectedLabels;
        set(this.args.oil.metadata, 'labels', selectedLabels);
        this.args.submit(this.args.oil);
    }

    @action
    updateAlternateNames() {
        this.args.submit(this.args.oil);
    }

    @action
    updateReference(event) {
        set(this.args.oil.metadata.reference, 'reference', event.target.value);
        this.args.submit(this.args.oil);
    }

    @action
    updateReferenceDate(event) {
        let enteredYear = event.target.value;

        if (isBlank(enteredYear)) {
            delete this.args.oil.metadata.reference.year;
        }
        else {
            set(this.args.oil.metadata.reference, 'year',
                Number(enteredYear));
        }

        this.args.submit(this.args.oil);
    }

    @action
    updateSampleReceivedDate(event) {
        let sampleDate = event.target.value;
        let currentYear = moment().utcOffset(0).year();

        if (sampleDate.match(/^\d{1,4}$/)) {
            // YYYY is a special case
            let year = parseInt(sampleDate.match(/^\d{1,4}/)[0]);
            if (year < 1900 || year > currentYear) sampleDate = '';

            set(this.args.oil.metadata, 'sample_date', sampleDate);
        }
        else {
            sampleDate = moment(sampleDate, 'YYYY-MM-DD')
                         .utcOffset(0).format('YYYY-MM-DD');

            if (sampleDate === 'Invalid date') sampleDate = '';

            if (sampleDate) {
                let year = parseInt(sampleDate.match(/^\d{4}/)[0]);
                if (year < 1900) sampleDate = '';
            }

            set(this.args.oil.metadata, 'sample_date', sampleDate);
        }

        this.args.submit(this.args.oil);
    }

    @action
    updateComments(event) {
        set(this.args.oil.metadata, 'comments', event.target.value);
        this.args.submit(this.args.oil);
    }

}
