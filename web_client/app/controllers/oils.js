import Controller from '@ember/controller';
import { action } from "@ember/object";
import { service } from '@ember/service';

export default class OilsController extends Controller {
    @service store;

    get canModifyDb() {
        return this.capabilities.toArray()[0].can_modify_db == 'true';
    }
    
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
    discardTemporaryEdits(oil, newRoute) {
        // reset the flag
        this.controllerFor('oils.show').changesMade = false;  // eslint-disable-line ember/no-controller-access-in-routes

        if (oil.oil_id.endsWith(this.tempSuffix)) {
            // switch back to the permanent model, discarding our changes.
            let permID = oil.oil_id.substring(0, oil.oil_id.length - this.tempSuffix.length);

            this.store.findRecord('oil', permID).then(function(permOil) {
                if (newRoute) {
                    this.transitionTo(newRoute);
                }
                else {
                    // keep the current route, but with the new ID
                    this.transitionTo('oils.show', permOil.id);
                }

                oil.deleteRecord();
                oil.save().then(function(result) {
                    result._internalModel.unloadRecord();
                }.bind(this));
            }.bind(this));
        }
    }




    @action
    createOil(oil) {
        let newOil = this.store.createRecord('oil', oil);
        let current_route = this.get('target');

        newOil.save().then(function(result) {
            // Success callback
            current_route.transitionTo('oils.show', result.id);
        }, function(errResult) {
            // Error callback
            let message = `Failed to save oil!!, ${errResult.error}`;
            console.error(message);
            window.alert(message);
        });
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
            if (!oilAttrs.oil_id.endsWith(this.tempSuffix)) {
                oilAttrs.oil_id = oilAttrs.oil_id.concat(this.tempSuffix);
            }

            let tempOil = this.store.createRecord('oil', oilAttrs);

            // transition to the temp object
            tempOil.save().then(function(result) {
                this.transitionTo('oils.show', result.id);
            }.bind(this));
        }
    }

    @action
    deleteOil(oil) {
        oil.deleteRecord();
        oil.save().then(function(result) {
            result._internalModel.unloadRecord();
            this.transitionTo('oils.index');
        }.bind(this));
    }

    @action
    error(error) {
        if (error.errors && error.errors[0] &&
                parseInt(error.errors[0].status) >= 100)
        {
            return true;
        }
        else {
            this.router.replaceWith('no-connection');
        }
    }

}
