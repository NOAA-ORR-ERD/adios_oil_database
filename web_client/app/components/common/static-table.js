import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';

export default class StaticTable extends Component {
    @tracked properties;

    constructor() {
        super(...arguments);

        this.readPropertyTypes(this.args.store, this.args.propertyName + ".json");
    }

    readPropertyTypes(store, propertyFileName) {
        return store.findRecord('config', 'sara-total-fractions.json')
        .then(function(response) {
            this.properties = response.template;
        }.bind(this));
    }
}
