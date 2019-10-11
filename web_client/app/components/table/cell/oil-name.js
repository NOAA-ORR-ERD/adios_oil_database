import Component from '@ember/component';

export default Component.extend({
  init() {
    this._super(...arguments);

    this.set('oilId', arguments[0].attrs.row.value.content.id);
  },

});
