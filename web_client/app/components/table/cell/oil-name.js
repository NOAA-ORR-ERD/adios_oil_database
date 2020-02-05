import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';

export default class OilName extends Component {
    @tracked oilId;

    constructor() {
        super(...arguments);

        this.oilId = this.args.row.content.id;
    }
}
