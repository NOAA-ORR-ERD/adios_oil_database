import Component from '@glimmer/component';
import { inject as service } from '@ember/service';
import { action } from "@ember/object";
import slugify from 'ember-slugify';

export default class Download extends Component {
    @service download;

    @action
    downloadOil() {
        let fileName = slugify(this.args.oil.name);

        this.download.asJSON(
            `${fileName}.json`,
            JSON.stringify(this.args.oil.serialize(), null, 2)
        );
    }
}
