import Component from '@ember/component';

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

        updateReference(event) {
            this.get('oil').set('reference', event.target.value);
        },

        updateReferenceDate() {
            //this.get('oil').set('referenceDate', Date.parse(event.target.value));
        },

        updateSampleReceivedDate() {
            //this.get('oil').set('sampleDate', Date.parse(event.target.value));
        }
    }
});
