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
            label: 'Status',
            valuePath: 'status',
            width: '70px',
            cellComponent: 'table/cell/status',
            searchable: true,
            align: "center",
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

    getQueryOptions() {
        let queryOptions = this.getProperties(['page',
            'limit',
            'sort',
            'dir',
            'q']);

        queryOptions['qLabels'] = this.selectedLabels.join();

        if (this.selectedApi.join() === '0,100') {
            // We are at the upper and lower limits of our slider control,
            // which we intend to mean that no API query options are specified.
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
