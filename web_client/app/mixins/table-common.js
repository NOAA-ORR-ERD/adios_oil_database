import { oneWay } from '@ember/object/computed';
import Mixin from '@ember/object/mixin';
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

  isLoading: oneWay('fetchRecords.isRunning'),
  canLoadMore: true,
  enableSync: true,

  model: null,
  data: null,
  meta: null,
  columns: null,
  table: null,

  init() {
    this._super(...arguments);

    this.set('data', []);

    let table = Table.create({
		columns: this.columns,
		rows: this.data,
		enableSync: this.enableSync
    });

    let sortColumn = table.get('allColumns').findBy('valuePath', this.sort);

    // Setup initial sort column
    if (sortColumn) {
      sortColumn.set('sorted', true);
    }

    this.set('table', table);
  },

  fetchRecords: task(function*() {
    let queryOptions = this.getQueryOptions();

    let records = yield this.store.query('oil', queryOptions);

    this.data.pushObjects(records.toArray());
    this.set('meta', records.get('meta'));

    this.set('canLoadMore', !isEmpty(records));
    this.incrementProperty('page');
  }).restartable(),

  getQueryOptions() {
      return {
          page: this.page,
          limit: this.limit,
          sort: this.sort,
          dir: this.dir
      }
  },

  actions: {
      onScrolledToBottom() {
          // We define this function because it seems to be required for
          // ember-light-table, but since we are loading the whole table
          // anyway, there is no need to check for any more records when
          // we scroll to the bottom
      },

      onColumnClick(column) {
          if (column.sorted) {
              this.setProperties({
                  dir: column.ascending ? 'asc' : 'desc',
                          sort: column.get('valuePath'),
                          canLoadMore: true,
                          page: 0
              });

              this.data.clear();
              this.set('page', 0);

              this.fetchRecords.perform();
          }
      }
  }
});

/* eslint-enable ember/no-new-mixins */
