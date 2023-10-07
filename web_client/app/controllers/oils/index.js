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

    get canModifyDb() {
        return this.capabilities.toArray()[0].can_modify_db == 'true';
    }
    
    get warningIgnoreList() {
        return this.configs.ignoreWarnings;
    }

    @action
    createOil(oil) {
        let newOil = this.store.createRecord('oil', oil);
        let current_route = this.get('target');

        newOil.save().then(function(result) {
            current_route.transitionTo('oils.show', result.id);
        }.bind(this));
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
