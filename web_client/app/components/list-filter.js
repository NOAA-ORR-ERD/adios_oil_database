import Component from '@ember/component';

export default Component.extend({
  classNames: ['list-filter'],
  value: '',

  init() {
    this._super(...arguments);
    this.filter('').then((allResults) => {
      this.set('results', allResults.results);
    });
  },

  actions: {
    handleFilterEntry() {
      let filterInputValue = this.value;
      let filterAction = this.filter;
      filterAction(filterInputValue).then((filterResults) => {
        if (filterResults.query === this.value) {
          this.set('results', filterResults.results);
        }
      });
    }
  }

});
