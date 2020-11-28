import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class GroupedTable extends Component {
    @tracked baseProperty = [];

    constructor() {
        super(...arguments);

        this.baseProperty = this.args.baseProperty;
    }

    @action
    addEmptyTableRow(index) {
        // index is the index on the table, not the index of the measurement
        // list.
        let basePropertyIdx;
        try {
            basePropertyIdx = this.args.items[index].index;
        }
        catch (TypeError) {
            // items index out of range.  Most likely we are trying to add a
            // row to the end of the list.
            basePropertyIdx = this.args.items[index - 1].index + 1;
        }

        let newEntry = {
            'groups': [this.args.group],
            'measurement': {},
        }

        this.baseProperty.splice(basePropertyIdx, 0, newEntry);
        this.baseProperty = this.baseProperty;

        this.updateValue(this.baseProperty);
    }

    @action
    deleteTableRow(index) {
        let basePropertyIdx = this.args.items[index].index;

        this.baseProperty.splice(basePropertyIdx, 1);
        this.baseProperty = this.baseProperty;

        this.updateValue(this.baseProperty);
    }

    @action
    updateValue(enteredValue) {
        this.args.submit(enteredValue);
    }

}
