import Component from '@ember/component';
import moment from 'moment';

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
            this.get('oil').samples.get(0).apis.set('0.gravity',  Number(event.target.value));
            //this.get('oil').save();
        },

        updateLocation(event) {
            //this.oil.location = event.target.value;
            this.get('oil').set('location', event.target.value);
        },

        updateType(event) {
            this.get('oil').set('productType', event.target.value);
        },

        updateCategories(selectedCategories) {
            this.set('selectedCategories', selectedCategories);  
            this.get('oil').set('categories', selectedCategories);
        },

        updateReference(event) {
            this.get('oil').set('reference', event.target.value);
        },

        updateReferenceDate(event) {
            this.get('oil').set('referenceDate', moment(event.target.value, "YYYY-MM-DD").tz("Europe/London").unix());
        },

        updateSampleReceivedDate(event) {
            this.get('oil').set('sampleDate', moment(event.target.value, "YYYY-MM-DD").tz("Europe/London").unix());
        },

        updateComments(event) {
            this.get('oil').set('comments', event.target.value);
        }
        
    }
});
