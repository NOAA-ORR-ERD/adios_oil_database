import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class ValueUnitTable extends Component {

    @tracked valueArray = [];

    constructor() {
        super(...arguments);

        this.tableId = this.args.tableTitle.replace(/\s+/g, '-').toLowerCase();

        this.valueArray = this.args.valueArray;
    }

    @action
    updateValue() {
        // TODO
    }
    
}