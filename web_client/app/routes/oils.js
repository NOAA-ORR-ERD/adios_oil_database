import Route from '@ember/routing/route';
import { hash } from 'rsvp';

export default Route.extend({
    model() {

        return hash({
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
        });
    },

    setupController(controller, models) {
        controller.setProperties(models);
    },

    actions: {
        updateOil(oil) {
            oil.save();
        },

        createOil(oil) {
            let newOil = this.store.createRecord('oil', oil);

            newOil.save().then(function(result) {
                this.transitionTo('oils.show', result.id);
            }.bind(this));
        },
        
        deleteOil(oil) {
            oil.deleteRecord();
            oil.save().then(function(result) {
                result._internalModel.unloadRecord();
                this.transitionTo('oils.index');
            }.bind(this));
        }
        
    }

});
