import Controller from '@ember/controller';

export default Controller.extend({
  actions: {
    filterByName(param) {
      if (param !== '') {
        return this.store.query('oil', { name: param })
          .then((results) => {
            return { query: param, results: results };
          });
      }
      else {
        return this.store.findAll('oil')
          .then((results) => {
            return { query: param, results: results };
          });
      }
    }
  }

});
