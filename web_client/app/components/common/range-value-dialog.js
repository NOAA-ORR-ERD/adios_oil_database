import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import { valueUnitUnit } from 'adios-db/helpers/value-unit-unit';
import { convertUnit } from 'adios-db/helpers/convert-unit';
import { valueUnit } from 'adios-db/helpers/value-unit';
import $ from 'jquery';

import Nucos from 'nucos/nucos';

const ESC_KEY = 27;


export default class RangeValueDialog extends Component {
    @tracked isInterval = false;

    @tracked unit;
    @tracked unitType;
    @tracked compatibleConverters;

    @tracked dialogValue = "";
    @tracked dialogMinValue = "";
    @tracked dialogMaxValue = "";

    constructor() {
        super(...arguments);
        this._initEscListener();

        //this.valueTitle = this.args.valueTitle;
        this.componentId = this.args.componentId;
        this.sourceValue = this.args.valueObject;

        this.numberStep = 1/Math.pow(10, this.args.valuePrecision);

        if (this.args.valueUnit.trim().length > 0) {
            this.unit = this.args.valueUnit.trim();
        }
        else {
            console.err("No unit or default unit defined!");
        }

        this.generateCompatibleConverters();

        this.unitType = this.compatibleConverters[0];

        if(this.sourceValue)
        {
            // check if there is a range value
            if(Number.isFinite(this.sourceValue.value)){
                this.dialogValue = valueUnit([convertUnit([this.sourceValue, this.args.valueUnit]),
                this.args.valuePrecision, true]);
                this.isInterval = false;
            } else {
                // always select interval input if there is no scalar value (?)
                let [valMin, valMax] = valueUnit([
                    convertUnit([this.sourceValue, this.args.valueUnit]),
                    this.args.valuePrecision,
                    true
                ]);

                this.dialogMinValue = valMin;
                this.dialogMaxValue = valMax;
                this.isInterval = true;
            }
        } else {
            this.dialogValue = "";
        }
        this.isShowingModal = true;
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

    get argNames() {
        return Object.keys(this.args);
    }

    get primaryUnitNames() {
        if (this.unitType) {
            let selected = Object.keys(this.unitType.PrimaryUnitNames).map(i => {
                return i === this.unitType.Synonyms[this.unit.toLowerCase().replace(/[\s.]/g, '')]
            });

            let unitNames = Object.values(this.unitType.PrimaryUnitNames);
            unitNames.splice(0, 0, '');

            if (selected.reduce((a, b) => a || b, false)) {
                // There was something selected.  Prepend an unselected
                // empty option
                selected.splice(0, 0, false);
            }
            else {
                // Nothing selected.  Prepend a selected empty option.
                selected.splice(0, 0, true);
            }

            return unitNames.map((v, i) => {
                return [v, selected[i]];
            });
        }
        else {
            return [];
        }
    }

    // add on ESC key event listener for dialog
    _initEscListener() {
        const closeOnEscapeKey = (ev) => {
            if (ev.keyCode === ESC_KEY) { 
                this.closeModalDialog(); 
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

    willDestroy() {
        super.willDestroy();

        $('body').off('keyup.modal-dialog');  // eslint-disable-line ember/no-jquery
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
    toggleRadio(isRange){
        this.isInterval = isRange;
   }

    @action
    closeModalDialog() {
        this.args.closeModalDialog();
    }

    @action
    changeValue(e) {
        if(Number.isNaN(parseFloat(e.target.value))) {
            this.dialogValue = "";
        } else {
            this.dialogValue = parseFloat(e.target.value);
        }
    }

    @action
    changeMin(e) {
        if(Number.isNaN(parseFloat(e.target.value))) {
            this.dialogMinValue = "";
        } else {
            this.dialogMinValue = parseFloat(e.target.value);  
        }
    }

    @action
    changeMax(e){
        if(Number.isNaN(parseFloat(e.target.value))) {
            this.dialogMaxValue = "";
        } else {
            this.dialogMaxValue = parseFloat(e.target.value);
        }
    }

    @action
    onSave(){
        let closeDialog = true;

        // check if input fileds are empty
        if (!this.isInterval && this.dialogValue === "" ||
            this.isInterval && this.dialogMinValue === "" &&
            this.dialogMaxValue === "")
        {

            let confirmMessage = "The input has no numeric value(s). If you save it " +
                this.args.valueTitle + " property will have no data in this oil record."
            if (!confirm(confirmMessage)) {
                closeDialog = false;
            }
        }

        if (closeDialog) {
            let enteredValue = {"unit": this.unit};

            if (this.isInterval) {
                if (this.dialogMinValue !== "") {
                    enteredValue["min_value"] = this.dialogMinValue;
                }
                if (this.dialogMaxValue !== "") {
                    enteredValue["max_value"] = this.dialogMaxValue;
                }
            } else {
                if (this.dialogValue !== "") {
                    enteredValue["value"] = this.dialogValue;
                }
            }

            this.args.updateValue(enteredValue);

            this.closeModalDialog();
        }
    }
}
