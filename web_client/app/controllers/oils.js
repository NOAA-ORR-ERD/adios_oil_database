import Controller from '@ember/controller';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class OilsController extends Controller {
    @action
    filterByName(param) {
        if (param !== '') {
            return this.store.query('oil', { name: param })
            .then((results) => {
                return { query: param, results: results };
            });
        }
        else {
            return this.store.findAll('oil')
            .then((results) => {
                return { query: param, results: results };
            });
        }
    }

}
