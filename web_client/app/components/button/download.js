import Component from '@glimmer/component';
import { service } from '@ember/service';
import { action } from "@ember/object";
import slugify from 'ember-slugify';

export default class Download extends Component {
    @service download;

    @action
    downloadOil() {
        let fileName = slugify(this.args.oil.metadata.name) + '_' + this.args.oil.oil_id;
        let content = this.args.oil.serialize();
        let oil = content['data']['attributes']

        this.download.asJSON(
            `${fileName}.json`,
            JSON.stringify(oil, null, 2)
        );
    }
}
