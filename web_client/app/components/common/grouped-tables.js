import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';

export default class GroupedTables extends Component {
    @tracked baseProperty;

    constructor() {
        super(...arguments);

        if (!this.args.oil[this.args.propertyName]) {
            this.args.oil[this.args.propertyName] = [];
        }

        this.baseProperty = this.args.oil[this.args.propertyName];
    }

    get tableGroups() {
        // We have a list of items that belong to one or more groups.
        // We want to turn it into a dict of grouped items
        return this.baseProperty.map( (c, i) => {
            if (c.groups) {
                return c.groups.map( (g) => {
                    return [g, c, i];
                });
            }
            else {
                return [['Ungrouped', c, i]];
            }
        })
        .reduce((acc, e) => {
            let [k, v, i] = e[0];
            acc[k] = (acc[k] ? acc[k]: []);
            acc[k].push({'value': v, 'index': i});
            return acc;
        }, {})
    }

}
