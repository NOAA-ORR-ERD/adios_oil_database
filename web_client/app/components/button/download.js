import Component from '@glimmer/component';
import { inject as service } from '@ember/service';
import { action } from "@ember/object";
import slugify from 'ember-slugify';

export default class Download extends Component {
    @service download;

    @action
    downloadOil() {
        let fileName = slugify(this.args.oil.metadata.name);
        let content = this.args.oil.serialize();
        let oil = content['data']['attributes']

        oil['_id'] = oil['metadata']['oil_id'] = this.args.oil.id;

        this.download.asJSON(
            `${fileName}.json`,
            JSON.stringify(oil, null, 2)
        );
    }
}
