import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import slugify from 'ember-slugify';

//
// Basically the logic for rendering columns vs. rows warrants two distinct
// table types.
// This is a wrapper for the respective column and row properties tables
// that passes only the necessary arguments to them.
//
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

        if (typeof this.args.headerPosition === 'undefined') {
            this.headerPosition = 'top';  // default
        }
        else {
            this.headerPosition = this.args.headerPosition;
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
}
