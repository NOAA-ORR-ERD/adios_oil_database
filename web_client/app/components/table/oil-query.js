import Component from '@ember/component';
import { computed } from '@ember/object';

import TableCommon from 'ember-oil-db/mixins/table-common';


export default Component.extend(TableCommon, {
    // our query option properties
    q: '',
    sort: 'metadata.name',
    limit: 50,

    columns: computed(function() {
        return [{
            label: 'Status',
            valuePath: 'status',
            resizable: true,
            minResizeWidth: 80,
            width: '5em',
            cellComponent: 'table/cell/status',
            classNames: 'text-nowrap',
            searchable: true,
            align: "center",
        }, {
            label: 'ID',
            valuePath: 'id',
            classNames: 'text-nowrap',
            width: '6em',
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
            width: '5em',
            minResizeWidth: 80,
            searchable: true,
            resizable: true,
        }, {
            label: 'API',
            valuePath: 'metadata.API',
            classNames: 'text-nowrap',
            cellComponent: 'table/cell/api',
            width: '4em',
            minResizeWidth: 60,
            resizable: true,
        }, {
            label: 'Score',
            valuePath: 'metadata.model_completeness',
            classNames: 'text-nowrap',
            width: '5em',
            minResizeWidth: 60,
            resizable: true,
        }, {
            label: 'Date',
            valuePath: 'metadata.sample_date',
            classNames: 'text-nowrap',
            cellComponent: 'table/cell/sample-date',
            width: '4em',
            minResizeWidth: 60,
            resizable: true,
        }
        // We will keep this around in comment form for debugging
        // should the need arise
        //{
        //    label: 'Labels',
        //    valuePath: 'metadata.labels',
        //    classNames: 'text-nowrap',
        //    cellComponent: 'table/cell/label',
        //    width: '9em',
        //    minResizeWidth: 100,
        //    resizable: true,
        //}
        ];
    }),

    init() {
        // this.savedFilters should be coming from the controller
        this.q = this.savedFilters['text'];
        this.selectedApi = this.savedFilters['api'];
        this.selectedLabels = this.savedFilters['labels'];
        this.sort = Object.keys(this.savedFilters['sort'])[0];
        this.dir = Object.values(this.savedFilters['sort'])[0];

        this._super(...arguments);

        this.set('labels', this.fetchLabels());
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
            this.savedFilters['text'] = this.q;
            this.savedFilters['api'] = this.selectedApi;
            this.savedFilters['labels'] = this.selectedLabels;

            this.data.clear();
            this.set('page', 0);
            this.fetchRecords.perform();
        },

        onColumnClick(column) {
            if (column.sorted) {
                let sort = column.get('valuePath');
                let dir = (column.ascending ? 'asc' : 'desc');

                this.savedFilters['sort'] = {[sort]: dir};

                this.setProperties({
                    dir: dir,
                    sort: sort,
                    canLoadMore: true,
                    page: 0
                });

                this.data.clear();
                this.set('page', 0);

                this.get('fetchRecords').perform();
            }
        }
    }
});
