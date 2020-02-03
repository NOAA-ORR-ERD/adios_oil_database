import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";
import slugify from 'ember-slugify';

export default class ListPropertiesTable extends Component {
    @tracked properties;
    @tracked baseProperty;

    constructor() {
        super(...arguments);
        let template;

        if (this.args.oil[this.args.propertyName]) {
            this.baseProperty = this.args.oil[this.args.propertyName];
        }
        else {
            this.baseProperty = {};
        }

        if (this.args.templateName) {
            // if we want to specify the template file name
            template = `${this.args.templateName}.json`;
        }
        else {
            // Otherwise use the slugified table title
            template = slugify(this.args.tableTitle, { separator: '_' }) + '.json';
        }
        
        if (typeof this.args.boldTitle === 'undefined') {
            this.boldTitle = true;  // default
        }
        else {
            this.boldTitle = this.args.boldTitle;
        }

        this.readPropertyTypes(this.args.store, template);
    }

    readPropertyTypes(store, template) {
        return store.findRecord('config', template, { reload: false })
        .then(function(response) {
            this.properties = response.template;
        }.bind(this));
    }

    get anyDataPresent() {
        if (this.properties && this.baseProperty) {
            return this.baseProperty.length > 0;
        }

        return false;
    }

    @action
    deleteTableRow(index) {
        this.baseProperty.splice(index, 1);
        this.baseProperty = this.baseProperty; // "reset" array for tracking

        this.updateValue(this.baseProperty);
    }

    @action
    addEmptyTableRow(index) {

        if (!this.baseProperty) {
            this.baseProperty = [];
        }

        this.baseProperty.splice(index, 0, {});
        this.baseProperty = this.baseProperty;

        this.updateValue(this.baseProperty);
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

        this.updateValue(this.baseProperty);
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

        this.updateValue(this.baseProperty);
    }

    @action
    updateValue(enteredValue) {
        if (Object.keys(enteredValue).length > 0) {
            set(this.args.oil, this.args.propertyName, enteredValue);
        }
        else {
            delete this.args.oil[this.args.propertyName];
        }

        this.args.submit(enteredValue);
    }
}
