import Component from '@ember/component';
import moment from 'moment';
import { isBlank , isNone} from '@ember/utils';

export default Component.extend({

    oilCategories: undefined,
    selectedCategories: undefined,

    init(){
        this._super(...arguments);
        this.set('oilCategories', this.getOilCategories());
        this.set('selectedCategories', this.oil.categories);
    },

    getOilCategories() {
        return this.oil.get('store').findAll('category')
            .then(function(response) {
                return response.toArray().map(i => {return i.name});
            });
    },
  
    actions: {
        updateAPI(event) {
            let oil = this.get('oil');
            let enteredAPI = event.target.value;
            if (isBlank(enteredAPI)) {
                delete oil.samples.get(0).apis;
            } else {
                if (isNone(oil.samples.get(0).apis)) {
                    oil.samples.get(0).apis = [{gravity: Number(enteredAPI)}];
                } else {
                    oil.samples.get(0).apis.set('0.gravity',  Number(enteredAPI));
                }
            }

            this.submit(oil);
        },

        updateLocation(event) {
            let oil = this.get('oil');
            oil.set('location', event.target.value);

            this.submit(oil);
        },

        updateType(event) {
            let oil = this.get('oil');
            oil.set('productType', event.target.value);

            this.submit(oil);
        },

        updateCategories(selectedCategories) {
            this.set('selectedCategories', selectedCategories);  

            let oil = this.get('oil');
            oil.set('categories', selectedCategories);

            this.submit(oil);
        },

        updateReference(event) {
            let oil = this.get('oil');
            oil.set('reference', event.target.value);

            this.submit(oil);
        },

        updateReferenceDate(event) {
            let oil = this.get('oil');
            oil.set('referenceDate', moment(event.target.value, "YYYY-MM-DD").tz("Europe/London").unix());

            this.submit(oil);
        },

        updateSampleReceivedDate(event) {
            let oil = this.get('oil');
            oil.set('sampleDate', moment(event.target.value, "YYYY-MM-DD").tz("Europe/London").unix());

            this.submit(oil);
        },

        updateComments(event) {
            let oil = this.get('oil');
            oil.set('comments', event.target.value);

            this.submit(oil);
        }
        
    }
});
