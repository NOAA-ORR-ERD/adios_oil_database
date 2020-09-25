import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import $ from 'jquery';

import Nucos from 'nucos/nucos';


export default class SelectUnitDialog extends Component {
    @tracked unit;
    @tracked unitType;
    @tracked compatibleConverters;

    constructor() {
        super(...arguments);

        this.unit = this.args.baseProperty.trim();
        
        if (!this.unit && this.args.defaultUnit) {
            this.unit = this.args.defaultUnit;
        }

        this.compatibleConverters = Object.values(Nucos.Converters).filter(c => {
            return c.Synonyms.hasOwnProperty((this.unit || '')
                    .toLowerCase()
                    .replace(/[\s.]/g, ''));
        });
        
        if (this.compatibleConverters) {
            this.unitType = this.compatibleConverters[0];
        }

    }

    get unitTypeNames() {
        return this.compatibleConverters.map((i) => {return i.Name});
    }

    get primaryUnitNames() {
        if (this.unitType) {
            let selected = Object.keys(this.unitType.PrimaryUnitNames).map(i => i === this.unitType.Synonyms[this.unit]);
            
            return Object.values(this.unitType.PrimaryUnitNames).map((v, i) => {
                return [v, selected[i]];
            });
        }
        else {
            return [];
        }
    }

    @action
    setModalEvents(element) {
        $(element).modal('show');
    }

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
            return (v === primaryName && k !== primaryName);})
            .map( ([k,]) => {return k})[0];

        this.unit = value;
    }

    @action
    closeModal() {
        this.args.closeModal();
    }

    @action
    submitForm() {
        this.closeModal();

        this.args.ok({'target': {'value': this.unit}});
    }

}
