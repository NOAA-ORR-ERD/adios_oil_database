import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import moment from 'moment';
import { isBlank , isNone} from '@ember/utils';

export default class Composition extends Component {
    @tracked oilCategories = undefined;
    @tracked selectedCategories = undefined;

    constructor() {
        super(...arguments);

        this.oilCategories = this.getOilCategories();
        this.selectedCategories = this.args.oil.categories;
    }

    getOilCategories() {
        return this.args.oil.store.findAll('category').then(function(response) {
            return response.toArray().map(i => {return i.name});
        });
    }

    @action
    updateAPI(event) {
        let enteredAPI = event.target.value;

        if (isBlank(enteredAPI)) {
            delete this.args.oil.samples.get(0).apis;
            // in case there is api on top level
            if (!isNone(this.args.oil.api)) {
                delete this.args.oil.api;
            }
        }
        else {
            if (isNone(this.args.oil.samples.get(0).apis)) {
                this.args.oil.samples.get(0).apis = [{gravity: Number(enteredAPI)}];
            }
            else {
                this.args.oil.samples.get(0).apis.set('0.gravity',  Number(enteredAPI));
            }

            this.args.oil.api = Number(enteredAPI);
        }

        this.args.submit(this.args.oil);
    }

    @action
    updateLocation(event) {
        this.args.oil.location = event.target.value;
        this.args.submit(this.args.oil);
    }

    @action
    updateType(event) {
        this.args.oil.productType = event.target.value;
        this.args.submit(this.args.oil);
    }

    @action
    updateCategories(selectedCategories) {
        this.selectedCategories = selectedCategories;
        this.args.oil.categories = selectedCategories;
        this.args.submit(this.args.oil);
    }

    @action
    updateReference(event) {
        this.args.oil.reference = event.target.value;
        this.args.submit(this.args.oil);
    }

    @action
    updateReferenceDate(event) {
        this.args.oil.referenceDate = moment(event.target.value, "YYYY-MM-DD")
            .tz("Europe/London").unix();
        this.args.submit(this.args.oil);
    }

    @action
    updateSampleReceivedDate(event) {
        this.args.oil.sampleDate = moment(event.target.value, "YYYY-MM-DD")
            .tz("Europe/London").unix();
        this.args.submit(this.args.oil);
    }

    @action
    updateComments(event) {
        this.args.oil.comments = event.target.value;
        this.args.submit(this.args.oil);
    }

}
