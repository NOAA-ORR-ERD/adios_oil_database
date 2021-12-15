import Route from '@ember/routing/route';
import { hash } from 'rsvp';
import { action } from "@ember/object";


export default class OilsRoute extends Route {
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

    @action
    commitTemporaryEdits(oil, newRoute) {
        // reset the flag
        this.controllerFor('oils.show').changesMade = false;  // eslint-disable-line ember/no-controller-access-in-routes

        if (oil.oil_id.endsWith(this.tempSuffix)) {
            // switch back to the permanent model, keeping our changes.
            let permID = oil.oil_id.substring(0, oil.oil_id.length - this.tempSuffix.length);
            this.store.findRecord('oil', permID).then(function(permOil) {
                // Update our permanent oil from the temp oil's properties
                oil.constructor.eachAttribute(function(key) {
                    if (key !== 'oil_id') {
                        permOil[key] = oil[key];
                    }
                }, this);

                permOil.save()
                .then(function(result) {
                    if (newRoute) {
                        this.transitionTo(newRoute);
                    }
                    else {
                        // keep the current route, but with the new ID
                        this.transitionTo('oils.show', result.id);
                    }
                }.bind(this))
                .then(function() {
                    oil.deleteRecord();
                    oil.save().then(function(result) {
                        result._internalModel.unloadRecord();
                    }.bind(this));
                }.bind(this));
            }.bind(this));
        }
    }

    @action
    discardTemporaryEdits(oil) {
        // reset the flag
        this.controllerFor('oils.show').changesMade = false;  // eslint-disable-line ember/no-controller-access-in-routes

        if (oil.oil_id.endsWith(this.tempSuffix)) {
            // switch back to the permanent model, discarding our changes.
            let permID = oil.oil_id.substring(0, oil.oil_id.length - this.tempSuffix.length);

            this.store.findRecord('oil', permID).then(function(permOil) {
                this.transitionTo('oils.show', permOil.id);

                oil.deleteRecord();
                oil.save().then(function(result) {
                    result._internalModel.unloadRecord();
                }.bind(this));
            }.bind(this));
        }
    }

    @action
    updateOil(oil) {
        let changesMade = this.controllerFor('oils.show').changesMade;  // eslint-disable-line ember/no-controller-access-in-routes

        if (changesMade) {
            // we are already in the editing context
            oil.save();
        }
        else {
            // we need to transition to the editing context
            this.controllerFor('oils.show').changesMade = true;  // eslint-disable-line ember/no-controller-access-in-routes

            // create a temporary oil object
            let oilAttrs = oil.serialize().data.attributes;
            oilAttrs.oil_id = oilAttrs.oil_id.concat(this.tempSuffix);

            let tempOil = this.store.createRecord('oil', oilAttrs);

            // transition to the temp object
            tempOil.save().then(function(result) {
                this.transitionTo('oils.show', result.id);
            }.bind(this));
        }
    }

    @action
    createOil(oil) {
        let newOil = this.store.createRecord('oil', oil);

        newOil.save().then(function(result) {
            this.transitionTo('oils.show', result.id);
        }.bind(this));
    }

    @action
    deleteOil(oil) {
        oil.deleteRecord();
        oil.save().then(function(result) {
            result._internalModel.unloadRecord();
            this.transitionTo('oils.index');
        }.bind(this));
    }
}
