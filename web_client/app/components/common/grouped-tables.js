import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';

export default class GroupedTables extends Component {
    @tracked baseProperty;

    constructor() {
        super(...arguments);
        if (this.args.oil[this.args.propertyName]) {
            this.baseProperty = this.args.oil[this.args.propertyName];
        }
        else {
            this.baseProperty = [];
        }
    }

    get tableGroups() {
        // We have a list of items that belong to one or more groups.
        // We want to turn it into a dict of grouped items
        return this.baseProperty.map( (c) => {
            return c.groups.map( (g) => {
                return [g, c];
            });
        })
        .reduce((acc, e) => {
            let [k, v] = e[0];
            acc[k] = (acc[k] ? acc[k]: []);
            acc[k].push(v);
            return acc;
        }, {})
    }

}
