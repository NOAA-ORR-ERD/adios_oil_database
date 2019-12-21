import Route from '@ember/routing/route';

export default Route.extend({
  model() {
      const oilsModel = this.modelFor('oils');

      return this.store.peekAll('oil', {param: oilsModel});
  }
});
