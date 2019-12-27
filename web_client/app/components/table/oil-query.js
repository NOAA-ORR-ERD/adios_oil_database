import Component from '@ember/component';
import { computed } from '@ember/object';
import { isEmpty } from '@ember/utils';
import { task } from 'ember-concurrency';

import TableCommon from 'ember-oil-db/mixins/table-common';


export default Component.extend(TableCommon, {
    // our query option properties
    q: '',

    columns: computed(function() {
        return [{
            label: '',
            valuePath: 'status',
            width: '30px',
            cellComponent: 'table/cell/status'
        }, {
            label: 'ID',
            valuePath: 'id',
            width: '100px',
            searchable: true,
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
            valuePath: 'api',
            cellComponent: 'table/cell/api',
            width: '70px'
        }, {
            label: 'Labels',
            valuePath: 'categories',
            cellComponent: 'table/cell/categories',
        }];
    }),

    init() {
        this._super(...arguments);

        this.labels = this.labels || [];
        this.selectedLabels = this.selectedLabels || [];
        this.set('labels', this.fetchLabels());

        this.selectedApi = this.selectedApi || [];
    },

    fetchLabels() {
        return this.get('store').findAll('category')
        .then(function(response) {
            return response.toArray().map(i => {return i.name});
        });
    },

    fetchRecords: task(function*() {
        let queryOptions = this.getQueryOptions();

        let records = yield this.get('store').query('oil', queryOptions);

        this.get('data').pushObjects(records.toArray());
        this.set('meta', records.get('meta'));

        this.set('canLoadMore', !isEmpty(records));

    }).restartable(),

    getQueryOptions() {
        let queryOptions = this.getProperties(['page',
            'limit',
            'sort',
            'dir',
            'q']);

        queryOptions['qLabels'] = this.selectedLabels.join();

        if (this.selectedApi.join() === '0,100') {
            // we are at the control limits, which we intend to mean
            // no API query options specified
            queryOptions['qApi'] = '';
        }
        else {
            queryOptions['qApi'] = this.selectedApi.join();
        }

        return queryOptions;
    },

    actions: {
        onSearchChange() {
            this.get('data').clear();
            this.set('page', 0);
            this.get('fetchRecords').perform();
        }
    }
});
