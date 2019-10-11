import Component from '@ember/component';
import { computed } from '@ember/object';
import { isEmpty } from '@ember/utils';
import { task } from 'ember-concurrency';

import TableCommon from 'ember-oil-db/mixins/table-common';


export default Component.extend(TableCommon, {
  q: '',

  // Filter Input Setup
  selectedFilter: computed.oneWay('possibleFilters.firstObject'),

  possibleFilters: computed('table.columns', function() {
    return this.get('table.columns').filterBy('searchable', true);
  }).readOnly(),

  columns: computed(function() {
    return [{
      label: '',
      valuePath: 'status',
      width: '30px',
      cellComponent: 'table/cell/status'
    }, {
      label: 'Name',
      valuePath: 'name',
      width: '230px',
      cellComponent: 'table/cell/oil-name',
      searchable: true,
    }, {
      label: 'Location',
      valuePath: 'location',
      width: '200px',
      searchable: true,
    }, {
      label: 'Type',
      valuePath: 'productType',
      width: '80px',
      searchable: true,
    }, {
      label: 'API',
      valuePath: 'apis',
      cellComponent: 'table/cell/api',
      width: '164px'
    }, {
      label: 'Viscosity',
      valuePath: 'viscosity',
      cellComponent: 'table/cell/viscosity',
      width: '120px'
    }, {
      label: 'Categories',
      valuePath: 'categories',
      cellComponent: 'table/cell/categories',
    }];
  }),

  fetchRecords: task(function*() {
    let queryOptions = this.getProperties(['page',
                                           'limit',
                                           'sort',
                                           'dir',
                                           'q',
                                           'selectedFilter.valuePath']);

    queryOptions['qAttr'] = queryOptions["selectedFilter.valuePath"];
    delete queryOptions["selectedFilter.label"];

    let records = yield this.get('store').query('oil', queryOptions);

    this.get('data').pushObjects(records.toArray());
    this.set('meta', records.get('meta'));

    this.set('canLoadMore', !isEmpty(records));
  }).restartable(),

  actions: {
    onSearchChange() {
      this.get('data').clear();
      this.set('page', 0);
      this.get('fetchRecords').perform();
    }
  }
});
