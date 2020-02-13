import { action, set } from "@ember/object";
import PropertiesTable from "./properties-table";

export default class ColumnListPropertiesTable extends PropertiesTable {

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
    updateListValue(index, attrName, unitValue) {
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
    updateListString(index, attrName, event) {
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
