import OilsController from '../oils';
import { tracked } from '@glimmer/tracking';


export default class IndexController extends OilsController {
    @tracked savedFilters = {
        'text': '',
        'api': [0, 100],
        'labels': [],
        'sort': {'metadata.name': 'asc'},
        'gnomeSuitable': false
    };

    get canModifyDb() {
        return this.capabilities.firstObject.can_modify_db == 'true';
    }
    
    get warningIgnoreList() {
        return this.configs.ignoreWarnings;
    }
}
