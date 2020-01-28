import Mixin from '@ember/object/mixin';
import { computed } from '@ember/object';
import { isEmpty } from '@ember/utils';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';
     
import Table from 'ember-light-table';

/* eslint-disable ember/no-new-mixins */

export default Mixin.create({
  store: service(),

  page: 0,
  limit: 20,
  dir: 'asc',
  sort: 'name',

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

    this.set('data', this.get('model').toArray());

    let table = Table.create({
		columns: this.get('columns'),
		rows: this.get('data'),
		enableSync: this.get('enableSync')
    });

    let sortColumn = table.get('allColumns').findBy('valuePath', this.get('sort'));

    // Setup initial sort column
    if (sortColumn) {
      sortColumn.set('sorted', true);
    }

    this.set('table', table);
  },

  fetchRecords: task(function*() {
    let queryOptions = this.getQueryOptions();

    let records = yield this.get('store').query('oil', queryOptions);

    this.get('data').pushObjects(records.toArray());
    this.set('meta', records.get('meta'));

    this.set('canLoadMore', !isEmpty(records));
    this.incrementProperty('page');
  }).restartable(),

  getQueryOptions() {
      return this.getProperties([
          'page',
          'limit',
          'sort',
          'dir'
      ]);
  },

  actions: {
    onScrolledToBottom() {
      if (this.get('canLoadMore')) {
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
        this.set('page', 0);
        this.get('fetchRecords').perform();
      }
    }
  }
});

/* eslint-enable ember/no-new-mixins */
