import Route from '@ember/routing/route';

export default Route.extend({
  model() {
      this.models = this.modelFor('oils');

      return this.store.peekAll('oil', {param: this.models.oil});
  },

  setupController(controller, model) {
      controller.set('labels', this.models.labels);
      controller.set('productTypes', this.models.productTypes);
      controller.set('capabilities', this.models.capabilities);
      
      this._super(controller, model);
  }
});
