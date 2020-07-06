import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import moment from 'moment';
import { isBlank } from '@ember/utils';

export default class OilDemographics extends Component {
    @tracked oilLabels = undefined;
    @tracked selectedLabels = undefined;

    constructor() {
        super(...arguments);

        this.oilLabels = this.getOilLabels();
        this.selectedLabels = this.args.oil.metadata.labels;
    }

    getOilLabels() {
        return this.args.oil.store.findAll('label').then(function(response) {
            return response.toArray().map(i => {return i.name});
        });
    }

    @action
    updateAPI(event) {
        let enteredAPI = event.target.value;

        if (isBlank(enteredAPI)) {
            delete this.args.oil.metadata.API;
        }
        else {
            this.args.oil.metadata.API = Number(enteredAPI);
        }

        this.args.submit(this.args.oil);
    }

    @action
    updateLocation(event) {
        this.args.oil.metadata.location = event.target.value;
        this.args.submit(this.args.oil);
    }

    @action
    updateType(event) {
        this.args.oil.metadata.product_type = event.target.value;
        this.args.submit(this.args.oil);
    }

    @action
    updateLabels(selectedLabels) {
        this.selectedLabels = selectedLabels;
        this.args.oil.metadata.labels = selectedLabels;
        this.args.submit(this.args.oil);
    }

    @action
    updateReference(event) {
        this.args.oil.metadata.reference = event.target.value;
        this.args.submit(this.args.oil);
    }

    @action
    updateReferenceDate(event) {
        this.args.oil.metadata.reference.year = event.target.value;
        this.args.submit(this.args.oil);
    }

    @action
    updateSampleReceivedDate(event) {
        this.args.oil.metadata.sample_date = (moment(event.target.value,
                                                     "YYYY-MM-DD")
                                              .tz("Europe/London").unix());
        this.args.submit(this.args.oil);
    }

    @action
    updateComments(event) {
        this.args.oil.metadata.comments = event.target.value;
        this.args.submit(this.args.oil);
    }

}
