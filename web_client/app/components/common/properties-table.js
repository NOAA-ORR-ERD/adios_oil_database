import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";
import slugify from 'ember-slugify';

export default class PropertiesTable extends Component {
    @tracked baseProperty;
    @tracked properties;

    constructor() {
        super(...arguments);

        this.initTemplateName();
        this.initBaseProperty();
        this.initBoldTitle();
        this.initBoldHeader();

        this.readPropertiesFromTemplate();
    }

    initBaseProperty() {
        let names = this.args.propertyName.split('.');
        
        
        this.baseProperty = this.args.oil;
        for (let i = 0; i < names.length; i++) {
            if (this.baseProperty[names[i]]) {
                this.baseProperty = this.baseProperty[names[i]];
            }
            else {
                this.baseProperty = this.baseProperty[names[i]] = {};
            }
        }
    }

    initBoldTitle() {
        if (typeof this.args.boldTitle === 'undefined') {
            this.boldTitle = true;  // default
        }
        else {
            this.boldTitle = this.args.boldTitle;
        }
    }

    initBoldHeader() {
        if (typeof this.args.boldHeader === 'undefined') {
            this.boldHeader = false;  // default
        }
        else {
            this.boldHeader = this.args.boldHeader;
        }
    }

    initTemplateName() {
        if (this.args.templateName) {
            // if we want to specify the template file name
            this.template = `${this.args.templateName}.json`;
        }
        else {
            // Otherwise use the slugified table title
            this.template = slugify(this.args.tableTitle, { separator: '_' }) + '.json';
        }

    }

    readPropertiesFromTemplate() {
        this.args.store.findRecord('config', this.template, { reload: false })
        .then(function(response) {
            this.properties = response.template;
        }.bind(this));
    }

    get anyDataPresent() {
        if (this.properties && this.baseProperty) {
            return Object.keys(this.properties).some(i => {
                return typeof this.baseProperty[i] !== 'undefined';
            });
        }

        return false;
    }

    @action
    updateAttrValue(attrName, unitValue) {
        if (unitValue) {
            if (!Number.isNaN(unitValue.value)) {
                set(this.baseProperty, attrName, unitValue);
            }
        }
        else {
            // empty value entered, remove the attribute
            delete this.baseProperty[attrName];
        }

        this.args.submit();
    }

    @action
    updateAttrString(attrName, event) {
        if (event.target.value) {
            set(this.baseProperty, attrName, event.target.value);
        }
        else {
            // empty value entered, remove the attribute
            delete this.baseProperty[attrName];
        }

        this.args.submit();
    }
}
