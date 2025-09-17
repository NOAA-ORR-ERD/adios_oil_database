import Component from '@glimmer/component';
import { action, set } from "@ember/object";
import { capitalize } from '@ember/string';
import slugify from 'ember-slugify';

export default class SubsampleMetadata extends Component {
    constructor() {
        super(...arguments);

        this.args.oil.metadata.fraction_evaporated = this.args.oil.metadata.fraction_evaporated||{};
    }

    get fractionEvaporatedUnitType() {
        let unitType = ((this.args.oil.metadata||{}).fraction_evaporated||{}).unit_type || '';

        return capitalize(unitType.substring(0, unitType.length - 'fraction'.length));
    }

    @action
    updateSampleName(event) {
        let sampleTab = '#' + slugify(`${event.target.value}`);
        this.args.updateSampleTab(sampleTab);
        this.args.updateCategoryTab(sampleTab + '-metadata');

        set(this.args.oil.metadata, 'short_name', event.target.value);

        this.args.submit(this.args.oil);
    }

    @action
    updateFractionEvaporated(fractionEvaporated) {
        set(this.args.oil.metadata, 'fraction_evaporated', fractionEvaporated);
        this.args.submit(this.args.oil);
    }

    @action
    updateDescription(event) {
        set(this.args.oil.metadata, 'description', event.target.value);
        this.args.submit(this.args.oil);
    }
}
