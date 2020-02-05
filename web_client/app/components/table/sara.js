import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";

export default class Sara extends Component {
    @tracked properties;
    @tracked saraArray;
    @tracked oil;

    constructor() {
        super(...arguments);

        this.oil = this.args.oil;
        this.saraArray = this.args.oil.sara_total_fractions;
        this.readPropertyTypes(this.args.store, 'sara_total_fractions.json');

    }

    readPropertyTypes(store, propertyFileName) {
        return store.findRecord('config', propertyFileName)
        .then(function(response) {
            this.properties = response.template;
        }.bind(this));
    }

    @action
    updateCellValue(label) {
        // TODO - rewrite this like getDeep/setDeep/removeDeep in range-value-input

        let index;
        if (this.saraArray) {
            index = this.saraArray.findIndex(x => x.sara_type === label);
        } else {
            index = -1;
        }

        if (index !== -1) {
            if(Number.isNaN(parseFloat(event.target.value))) {
                // empty value entered
                this.saraArray.splice(index, 1);
            } else {
                set(this.saraArray[index].fraction, "value", Number(event.target.value));
                // TODO - cannot figure out which value we shoud take - percent or fraction
                set(this.saraArray[index], "percent", Number(event.target.value));
            }
        } else {
            // there is no object with such property type
            if(!Number.isNaN(parseFloat(event.target.value))) {
                let saraItem = {
                    sara_type: label,
                    percent: Number(event.target.value),
                    fraction: {
                        value: Number(event.target.value),
                        unit: "%"
                    }
                };
                if(!this.saraArray) {
                    this.saraArray = [];
                }
                this.saraArray.push(saraItem);
            }
        }

        if (this.saraArray && this.saraArray.length !== 0) {
            set(this.oil, "sara_total_fractions", this.saraArray);
        } else {
            if (this.oil.sara_total_fractions) {
                delete this.oil.sara_total_fractions;
            }
        }

        this.args.submit(this.oil);
    }

}
