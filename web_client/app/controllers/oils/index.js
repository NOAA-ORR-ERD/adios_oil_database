import OilsController from '../oils';
import { tracked } from '@glimmer/tracking';


export default class IndexController extends OilsController {
    @tracked savedFilters = {
        'text': '',
        'api': [0, 100],
        'labels': []
    }
}
