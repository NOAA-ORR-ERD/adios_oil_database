import ApplicationRoute from './application';
import { hash } from 'rsvp';
import { action } from "@ember/object";


export default class OilsRoute extends ApplicationRoute {
    tempSuffix = '-TEMP';

    model() {
        return hash({
            configs: (async () => {
                return this.store.findRecord('config', 'main.json');
            })(),

            oils: (async () => {
                let config = await this.store.findRecord('config', 'main.json');
                var adapter = await this.store.adapterFor('oil');

                if (adapter.host !== config.webApi) {
                  adapter = await adapter.reopen({host: config.webApi});
                }

                return this.store.peekAll('oil');
            })(),

            labels: (async () => {
                let config = await this.store.findRecord('config', 'main.json');
                var adapter = await this.store.adapterFor('label');

                if (adapter.host !== config.webApi) {
                  adapter = await adapter.reopen({host: config.webApi});
                }

                return this.store.findAll('label');
            })(),

            productTypes: (async () => {
                let config = await this.store.findRecord('config', 'main.json');
                var adapter = await this.store.adapterFor('product-type');

                if (adapter.host !== config.webApi) {
                  adapter = await adapter.reopen({host: config.webApi});
                }

                return this.store.findAll('product-type');
            })(),

            capabilities: (async () => {
                let config = await this.store.findRecord('config', 'main.json');
                var adapter = await this.store.adapterFor('capability');

                if (adapter.host !== config.webApi) {
                  adapter = await adapter.reopen({host: config.webApi});
                }

                return this.store.findAll('capability');
            })(),
        });
    }

    setupController(controller, models) {
        controller.setProperties(models);
    }

}
