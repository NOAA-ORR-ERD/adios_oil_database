import OilsController from '../oils';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";


export default class IndexController extends OilsController {
    @tracked savedFilters = {
        'text': '',
        'api': [0, 100],
        'labels': [],
        'sort': {'metadata.name': 'asc'},
        'gnomeSuitable': false
    };

    get warningIgnoreList() {
        return this.configs.ignoreWarnings;
    }

}
