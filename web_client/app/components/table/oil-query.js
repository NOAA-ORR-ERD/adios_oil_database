import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action, setProperties } from "@ember/object";

import { inject as service } from '@ember/service';
import { isEmpty } from '@ember/utils';
import { task } from 'ember-concurrency';

import Table from 'ember-light-table';


export default class NewOilQuery extends Component {
    @service store;
    enableSync = false;

    // our query option properties
    @tracked q;
    @tracked sort = 'metadata.name';
    @tracked dir = 'asc';
    @tracked meta;
    @tracked selectedType;
    @tracked gnomeSuitable;

    page = 0;
    limit = 50;    
    canLoadMore = true;
    data = [];

    get isLoading() {
        return this.fetchRecords.isRunning;
    }

    columns = [{
        label: 'Status',
        valuePath: 'status',
        cellComponent: 'table/cell/status',
        width: '5em',
        minResizeWidth: 80,
        classNames: 'text-nowrap',
        resizable: true,
        searchable: true,
        align: "center",
    }, {
        label: 'ID',
        valuePath: 'id',
        width: '5em',
        minResizeWidth: 75,
        classNames: 'text-nowrap',
        searchable: true,
        resizable: true,
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
        minResizeWidth: 100,
        classNames: 'text-nowrap',
        searchable: true,
        resizable: true,
    }, {
        label: 'Product Type',
        valuePath: 'metadata.product_type',
        width: '12em',
        minResizeWidth: 80,
        classNames: 'text-nowrap',
        searchable: true,
        resizable: true,
    }, {
        label: 'API',
        valuePath: 'metadata.API',
        cellComponent: 'table/cell/api',
        width: '4em',
        minResizeWidth: 60,
        classNames: 'text-nowrap',
        resizable: true,
    }, {
        label: 'Score',
        valuePath: 'metadata.model_completeness',
        width: '5em',
        minResizeWidth: 60,
        classNames: 'text-nowrap',
        resizable: true,
    }, {
        label: 'Date',
        valuePath: 'metadata.sample_date',
        cellComponent: 'table/cell/sample-date',
        width: '4em',
        minResizeWidth: 60,
        classNames: 'text-nowrap',
        resizable: true,
    }];
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

    constructor() {
        super(...arguments);

        // this.args.savedFilters should be coming from the controller
        this.q = this.args.savedFilters['text'];
        this.selectedApi = this.args.savedFilters['api'];
        this.selectedType = this.args.savedFilters['product_type'];
        this.selectedLabels = this.args.savedFilters['labels'];
        this.selectedGnomeSuitable = this.args.savedFilters['gnomeSuitable'];
        this.sort = Object.keys(this.args.savedFilters['sort'])[0];
        this.dir = Object.values(this.args.savedFilters['sort'])[0];

        this.table = Table.create({
            columns: this.columns,
            rows: this.data,
            enableSync: this.enableSync
        });

        let sortColumn = this.table.allColumns.findBy('valuePath', this.sort);

        // Setup initial sort column
        if (sortColumn) {
          sortColumn.set('sorted', true);
        }

        this.fetchRecords.perform();
    }

    get filteredLabels() {
        let productType = this.selectedType;

        if (productType === 'None') {productType = ''}

        if (productType) {
            return this.args.labels.filter(i => {
                return i.product_types.includes(productType);
            }).mapBy('name');
        }
        else {
            return this.args.labels.mapBy('name');
        }
    }

    get queryOptions() {
        let queryOptions = {
                page: this.page,
                limit: this.limit,
                sort: this.sort,
                dir: this.dir,
                q: this.q
        };

        queryOptions['qLabels'] = this.selectedLabels.join();

        if (this.selectedType) {
            queryOptions['qType'] = this.selectedType;
        }

        if (this.selectedApi.join() === '0,100') {
            // We are at the upper and lower limits of our slider control,
            // which we intend to mean that no API query options are specified.
            queryOptions['qApi'] = '';
        }
        else {
            queryOptions['qApi'] = this.selectedApi.join();
        }

        if (this.selectedGnomeSuitable) {
            queryOptions['qGnomeSuitable'] = this.selectedGnomeSuitable;
        }

        return queryOptions;
    }

    @(task(function*() {
        while (this.canLoadMore) {
            let records = yield this.store.query('oil', this.queryOptions);

            this.meta = records.meta;
            this.data.pushObjects(records.toArray());
            yield this.table.pushRows(records.toArray());

            this.page++;
            this.canLoadMore = !isEmpty(records);
        }
    }).restartable()) fetchRecords;

    @action onSearchChange() {
        this.args.savedFilters['text'] = this.q;
        this.args.savedFilters['api'] = this.selectedApi;
        this.args.savedFilters['product_type'] = this.selectedType;
        this.args.savedFilters['labels'] = this.selectedLabels;
        this.args.savedFilters['gnomeSuitable'] = this.selectedGnomeSuitable;

        this.data.clear();
        this.table.setRows([]);
        this.page = 0;
        this.canLoadMore = true;

        this.fetchRecords.perform();
    }

    @action onColumnClick(column) {
        let sort, dir;

        if (this.sort === column.valuePath) {
            // we already clicked on this before
            sort = this.sort;
            dir = (this.dir === 'asc' ? 'desc' : 'asc');
        }
        else {
            // newly clicked column
            sort = column.valuePath;
            dir = 'asc';
        }

        this.args.savedFilters['sort'] = {[sort]: dir};

        setProperties(this, {
            dir: dir,
            sort: sort,
            canLoadMore: true,
            page: 0
        });

        this.data.clear();
        this.table.setRows([]);
        this.page = 0;
        this.canLoadMore = true;

        this.fetchRecords.perform();
    }

    @action onTypeSelected(event) {
        this.selectedType = event.target.value === 'None' ? '' : event.target.value;
    }
}
