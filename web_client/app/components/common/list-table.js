import PropertiesTable from './properties-table';

import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";

import slugify from 'ember-slugify';


export default class ListTable extends PropertiesTable {
    @tracked baseProperty;

    constructor() {
        super(...arguments);
    }

    @action
    deleteTableRow(index) {
        this.baseProperty.splice(index, 1);
        this.baseProperty = this.baseProperty; // "reset" array for tracking
        this.syncBaseProperty();

        this.args.submit();
    }

    @action
    addEmptyTableRow(index) {
        this.baseProperty.splice(index, 0, '');
        this.baseProperty = this.baseProperty;
        this.syncBaseProperty();

        this.args.submit();
    }

    @action
    updateListValue(index, unitValue) {
        if (unitValue) {
            if (!Number.isNaN(unitValue.value)) {
                this.baseProperty[index] = unitValue;
                this.baseProperty = this.baseProperty;
                this.syncBaseProperty();
            }
        }

        this.args.submit();
    }

    @action
    updateListString(index, event) {
        if (event.target.value) {
            this.baseProperty[index] = event.target.value;
            this.baseProperty = this.baseProperty;
            this.syncBaseProperty();
        }

        this.args.submit();
    }
}
