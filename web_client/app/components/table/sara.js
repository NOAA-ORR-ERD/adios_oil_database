import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";

export default class Sara extends Component {
    @tracked properties;
    @tracked oil;

    constructor() {
        super(...arguments);

        this.oil = this.args.oil;
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
        // we need to work with oil.SARA.{{label}} as a property

        if (!this.oil.SARA) {
            set(this.oil, 'SARA', {});
        }

        let saraItem = {
            value: Number(event.target.value),
            unit: '%',
            unit_type: 'massfraction'
         };

        set(this.oil.SARA, label.toLowerCase(), saraItem);

        this.args.submit(this.oil);
    }
}
