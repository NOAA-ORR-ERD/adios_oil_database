import Mixin from '@ember/object/mixin';
import { computed } from '@ember/object';
import { isEmpty } from '@ember/utils';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';
     
import Table from 'ember-light-table';


export default Mixin.create({
  store: service(),

  page: 0,
  limit: 10,
  dir: 'asc',
  sort: 'firstName',

  isLoading: computed.oneWay('fetchRecords.isRunning'),
  canLoadMore: true,
  enableSync: true,

  model: null,
  data: null,
  meta: null,
  columns: null,
  table: null,

  init() {
    this._super(...arguments);

    this.set('data',this.get('model').toArray());

    let table = new Table(this.get('columns'),
                          this.get('data'),
                          { enableSync: this.get('enableSync') });
    let sortColumn = table.get('allColumns').findBy('valuePath', this.get('sort'));

    // Setup initial sort column
    if (sortColumn) {
      sortColumn.set('sorted', true);
    }

    this.set('table', table);
  },

  fetchRecords: task(function*() {
    let records = yield this.get('store').query(
      'oil',
      this.getProperties(['page',
                          'limit',
                          'sort',
                          'dir'])
    );

    this.get('data').pushObjects(records.toArray());
    this.set('meta', records.get('meta'));

    this.set('canLoadMore', !isEmpty(records));
  }).restartable(),

  actions: {
    onScrolledToBottom() {
      if (this.get('canLoadMore')) {
        this.incrementProperty('page');
        this.get('fetchRecords').perform();
      }
    },

    onColumnClick(column) {
      if (column.sorted) {
        this.setProperties({
          dir: column.ascending ? 'asc' : 'desc',
          sort: column.get('valuePath'),
          canLoadMore: true,
          page: 0
        });
        this.get('data').clear();
        this.get('fetchRecords').perform();
      }
    }
  }
});
