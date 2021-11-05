import BaseComponent from './base-component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";
import slugify from 'ember-slugify';

export default class PropertiesTable extends BaseComponent {
    @tracked baseProperty;
    @tracked properties;

    deep_value = (obj, path, defaultVal) => path.split(".").reduce((o, key) => o && o[key] ? o[key] : defaultVal, obj);

    constructor() {
        super(...arguments);

        this.initTemplateName();
        this.readPropertiesFromTemplate();

        this.initBaseProperty();
        this.initBoldTitle();
        this.initBoldHeader();
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

    initBaseProperty() {
        this.baseProperty = this.deep_value(this.args.oil, this.args.propertyName, []);
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

    syncBaseProperty() {
        // reattach baseProperty to the oil property
        let names = this.args.propertyName.split('.');
        let tempProperty = this.args.oil;

        if (names.length > 1) {
            for (let i = 0; i < names.length - 1; i++) {
                if (tempProperty[names[i]]) {
                    tempProperty = tempProperty[names[i]];
                }
                else {
                    tempProperty = tempProperty[names[i]] = {};
                }
            }
        }

        set(tempProperty, names.lastObject, this.baseProperty);
    }

    // Our oil model generates sparse json records.  So there could be entire
    // sub-branches of our record that are missing.  When this happens,
    // our edit controls can't attach to the record, and the edits are lost.
    // This is a convenience function that will create a branch in our record
    // using the base oil object and a property string.
    setAttrsIfMissing() {
        if (!this.deepGet(this.args.oil, this.args.propertyName)) {
            this.deepSet(this.args.oil, this.args.propertyName, []);
        }
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
