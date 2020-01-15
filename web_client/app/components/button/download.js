import Component from '@glimmer/component';
import { inject as service } from '@ember/service';
import { action } from "@ember/object";

export default class Download extends Component {
    @service download;

    @action
    downloadOil() {
        this.download.asJSON(
            `${this.args.oil.name}.json`,
            JSON.stringify(this.args.oil.serialize(), null, 2)
        );
    }
}
