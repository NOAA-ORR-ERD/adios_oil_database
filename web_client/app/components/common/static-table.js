import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";
import slugify from 'ember-slugify';

export default class StaticTable extends Component {
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
        return store.findRecord('config', template)
        .then(function(response) {
            this.properties = response.template;
        }.bind(this));
    }

    get anyDataPresent() {
        if (this.properties && this.baseProperty) {
            return Object.keys(this.properties).some(i => {
                return this.baseProperty.hasOwnProperty(i);
            });
        }

        return false;
    }

    @action
    updateCellValue(attr) {
        if (event.target.value === '') {
            // empty value entered, remove the attribute
            delete this.baseProperty[attr];
        }
        else {
            let newValue = parseFloat(event.target.value);

            if (!Number.isNaN(newValue)) {
                set(this.baseProperty, attr, {
                    value: newValue,
                    unit: this.args.valueUnit
                });
            }
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
