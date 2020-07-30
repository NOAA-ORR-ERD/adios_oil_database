import Component from '@ember/component';
import { computed } from '@ember/object';

import TableCommon from 'ember-oil-db/mixins/table-common';


export default Component.extend(TableCommon, {
    // our query option properties
    q: '',
    sort: 'metadata.name',

    columns: computed(function() {
        return [{
            label: 'Status',
            valuePath: 'status',
            resizable: true,
            minResizeWidth: 80,
            width: '80px',
            cellComponent: 'table/cell/status',
            classNames: 'text-nowrap',
            searchable: true,
            align: "center",
        }, {
            label: 'ID',
            valuePath: 'id',
            classNames: 'text-nowrap',
            width: '110px',
            searchable: true,
            resizable: true,
            minResizeWidth: 75
        }, {
            label: 'Name',
            valuePath: 'metadata.name',
            cellComponent: 'table/cell/oil-name',
            classNames: 'text-nowrap',
            searchable: true,
            minResizeWidth: 100,
            resizable: true,
        }, {
            label: 'Location',
            valuePath: 'metadata.location',
            classNames: 'text-nowrap',
            searchable: true,
            minResizeWidth: 100,
            resizable: true,
        }, {
            label: 'Type',
            valuePath: 'metadata.product_type',
            classNames: 'text-nowrap',
            width: '100px',
            minResizeWidth: 80,
            searchable: true,
            resizable: true,
        }, {
            label: 'API',
            valuePath: 'metadata.API',
            classNames: 'text-nowrap',
            cellComponent: 'table/cell/api',
            width: '80px',
            minResizeWidth: 60,
            resizable: true,
        }, {
            label: 'Labels',
            valuePath: 'metadata.labels',
            classNames: 'text-nowrap',
            cellComponent: 'table/cell/label',
            width: '150px',
            minResizeWidth: 100,
            resizable: true,
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
        return this.store.findAll('label')
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
            this.data.clear();
            this.set('page', 0);
            this.fetchRecords.perform();
        }
    }
});
