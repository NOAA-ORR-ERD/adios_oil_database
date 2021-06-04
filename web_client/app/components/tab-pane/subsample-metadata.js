import Component from '@glimmer/component';
import { action, set } from "@ember/object";
import { capitalize } from '@ember/string';


export default class SubsampleMetadata extends Component {
    get fractionEvaporatedUnitType() {
        let unitType = this.args.oil.metadata.fraction_evaporated.unit_type || '';
        return capitalize(unitType.substring(0, unitType.length - 'fraction'.length));
    }

    @action
    updateDescription(event) {
        set(this.args.oil.metadata, 'description', event.target.value);
        this.args.submit(this.args.oil);
    }
}
