import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import $ from 'jquery';

import Nucos from 'nucos/nucos';

const ESC_KEY = 27;


export default class SelectUnitDialog extends Component {
    @tracked unit;
    @tracked unitType;
    @tracked compatibleConverters;

    constructor() {
        super(...arguments);
        this._initEscListener();

        this.unit = this.args.baseProperty.trim();

        if (!this.unit && this.args.defaultUnit) {
            this.unit = this.args.defaultUnit;
        }

        this.generateCompatibleConverters();

        if (this.args.unitType) {
            let compatList = this.compatibleConverters.filter(c => {
                return c.Name.replace(/\s/g, '').toLowerCase() === this.args.unitType;
            });

            this.unitType = compatList[0];
        }
        else if (this.compatibleConverters) {
            this.unitType = this.compatibleConverters[0];
        }
    }

    // add on ESC key event listener for dialog
    _initEscListener() {
        const closeOnEscapeKey = (ev) => {
            if (ev.keyCode === ESC_KEY) {
                this.closeModal();
            }
        };

        // Note: Ember doesn't want you to use JQuery for some purity reason,
        //       and it throws warnings when the app starts.
        //       But this is the recommended way to add an escape listener
        //       to an ember-modal-dialog according to their README.
        //
        //       https://github.com/yapplabs/ember-modal-dialog#keyboard-shortcuts
        $('body').on('keyup.modal-dialog', closeOnEscapeKey);  // eslint-disable-line ember/no-jquery
    }
    
    generateCompatibleConverters() {
        if (this.unit) {
            this.compatibleConverters = Object.values(Nucos.Converters).filter(c => {
                return c.Synonyms.hasOwnProperty(
                    (this.unit || '').toLowerCase().replace(/[\s.]/g, '')
                );
            });
        }
        else {
            this.compatibleConverters = Object.values(Nucos.Converters);
        }
    }

    get unitTypeNames() {
        let ret = this.compatibleConverters.map((i) => {
            return [i.Name, i.Name === this.unitType.Name]
        });

        if (ret.length > 0 && !ret.reduce((a, b) => a || b[1], 0)) {
            // No matches with current unit type.  Set the first item
            ret[0][1] = true;
        }

        return ret;
    }

    get primaryUnitNames() {
        if (this.unitType) {
            let selected = Object.keys(this.unitType.PrimaryUnitNames).map(i => {
                return i === this.unitType.Synonyms[this.unit]
            });

            let unitNames = Object.values(this.unitType.PrimaryUnitNames);
            unitNames.insertAt(0, "");
            
            if (selected.reduce((a, b) => a || b, false)) {
                // There was something selected.  Prepend an unselected
                // empty option
                selected.insertAt(0, false);
            }
            else {
                // Nothing selected.  Prepend a selected empty option.
                selected.insertAt(0, true);
            }

            return unitNames.map((v, i) => {
                return [v, selected[i]];
            });
        }
        else {
            return [];
        }
    }

    //@action
    //setModalEvents(element) {
    //    $(element).modal('show');
    //}

    @action
    updateUnitType(event) {
        let matched = Object.values(this.compatibleConverters).filter(c => {
            return c.Name === event.target.value;
        });

        if (matched) {
            this.unitType = matched[0];
        }
        else {
            this.unitType = null;
        }
    }

    @action
    updateUnit(event) {
        let primaryName = Object.keys(this.unitType.PrimaryUnitNames).find(key => {
            return this.unitType.PrimaryUnitNames[key] === event.target.value;
        });

        let value = Object.entries(this.unitType.Synonyms).filter( ([k, v]) => {
            return (v === primaryName && k !== primaryName);
        }).map(([k,]) => {
            return k
        })[0];

        this.unit = value;

        // invoke a new unit type list
        this.generateCompatibleConverters();
    }

    @action
    closeModal() {
        this.args.closeModal();
    }

    @action
    submitForm() {
        this.closeModal();

        this.args.ok({'target': {
            'value': this.unit,
            'unit_type': this.unitType.Name
        }});
    }

}
