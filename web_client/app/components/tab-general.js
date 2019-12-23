import Component from '@ember/component';

export default Component.extend({

    // oilCategories: ['one', 'two', 'three', 'four'],

    // init(){
    //     this._super(...arguments);
    //     this.set('oilCategories', this.fetchOilCategories());
    // },

    // fetchOilCategories() {
    //     return this.get('store').findAll('category')
    //            .then(function(response) {
    //                return response.toArray().map(i => {return i.name});
    //            });
    // },
  
    actions: {
        updateAPI() {
            alert('API value has been changed!');
        }
    }
});
