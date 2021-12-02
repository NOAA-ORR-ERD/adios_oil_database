import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class GroupedTable extends Component {
    @tracked baseProperty = [];
    @tracked items;

    constructor() {
        super(...arguments);

        this.baseProperty = this.args.baseProperty;
        
        if (this.args.items) {
            this.items = this.args.items;
        }
        else {
            this.items = [];
        }
    }

    @action
    addEmptyTableRow(index) {
        // index is the index on the table, not the index of the measurement
        // list.
        let basePropertyIdx;
        
        try {
            basePropertyIdx = this.items[index].index;
        }
        catch (TypeError) {
            // items index out of range.
            if (index === 0) {
                // we are dealing with an empty table
                basePropertyIdx = 0;
            }
            else {
                // Most likely we are trying to add a row to the end
                // of the list.
                basePropertyIdx = this.items[index - 1].index + 1;
            }
        }

        let newEntry = {
            'groups': [this.args.group],
            'measurement': {
                unit_type: 'massfraction',
                unit: '1'
            },
        }

        this.baseProperty.splice(basePropertyIdx, 0, newEntry);
        this.baseProperty = this.baseProperty;

        this.updateValue(this.baseProperty);
    }

    @action
    deleteTableRow(index) {
        let basePropertyIdx = this.items[index].index;

        this.baseProperty.splice(basePropertyIdx, 1);
        this.baseProperty = this.baseProperty;

        this.updateValue(this.baseProperty);
    }

    @action
    updateValue(enteredValue) {
        this.args.submit(enteredValue);
    }

}
