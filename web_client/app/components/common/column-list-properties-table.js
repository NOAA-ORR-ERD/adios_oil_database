import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";

export default class ColumnListPropertiesTable extends Component {
    @tracked baseProperty;

    constructor() {
        super(...arguments);

        if (this.args.baseProperty) {
            this.baseProperty = this.args.baseProperty;
        }

        if (typeof this.args.boldTitle === 'undefined') {
            this.boldTitle = true;  // default
        }
        else {
            this.boldTitle = this.args.boldTitle;
        }
    }

    get anyDataPresent() {
        if (this.baseProperty) {
            return this.baseProperty.length > 0;
        }

        return false;
    }

    @action
    deleteTableRow(index) {
        this.baseProperty.splice(index, 1);
        this.baseProperty = this.baseProperty; // "reset" array for tracking

        this.args.submit();
    }

    @action
    addEmptyTableRow(index) {

        if (!this.baseProperty) {
            this.baseProperty = [];
        }

        this.baseProperty.splice(index, 0, {});
        this.baseProperty = this.baseProperty;

        this.args.submit();
    }

    @action
    updateCellValue(index, attrName, unitValue) {
        if (unitValue) {
            if (!Number.isNaN(unitValue.value)) {
                set(this.baseProperty[index], attrName, unitValue);
            }
        }
        else {
            // empty value entered, remove the attribute
            delete this.baseProperty[index][attrName];
        }

        this.args.submit();
    }

    @action
    updateCellString(index, attrName, event) {
        if (event.target.value) {
            set(this.baseProperty[index], attrName, event.target.value);
        }
        else {
            // empty value entered, remove the attribute
            delete this.baseProperty[index][attrName];
        }

        this.args.submit();
    }
}
