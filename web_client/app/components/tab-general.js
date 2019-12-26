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
        updateAPI() {
            alert('API value has been changed!');
        },

        updateLocation(event) {
            //this.oil.location = event.target.value;
            this.get('oil').set('location', event.target.value);
            //this.get('oil').save();
        },

        updateReference() {

        },

        updateReferenceDate() {

        },

        updateSampleReceivedDate() {

        }
    }
});
