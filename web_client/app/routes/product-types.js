import Route from '@ember/routing/route';
import { action } from "@ember/object";

export default class ProductTypesRoute extends Route {
    model() {
        return (async () => {
            let config = await this.store.findRecord('config', 'main.json');
            var adapter = await this.store.adapterFor('product-type');

            if (adapter.host !== config.webApi) {
              adapter = await adapter.reopen({host: config.webApi});
            }

            return this.store.findAll('product-type');
        })();
    }

    @action
    error() {
        this.replaceWith('no-connection');
    }

}
