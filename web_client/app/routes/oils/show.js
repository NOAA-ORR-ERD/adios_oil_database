import Route from '@ember/routing/route';
import { action } from "@ember/object";
import slugify from 'ember-slugify';


export default class OilsShowRoute extends Route {
    model(params) {
        this.models = this.modelFor('oils');

        return this.store.findRecord('oil', params.oil_id,
                                     {param: this.models.oil, reload: true });
    }

    setupController(controller, model) {
        super.setupController(controller, model);

        controller.set('labels', this.models.labels);
        controller.set('productTypes', this.models.productTypes);
        controller.set('capabilities', this.models.capabilities);
        controller.set('distillationTypes', [
            'mass fraction',
            'volume fraction',
            'unknown'
        ]);


        // Our current sample tabs at the start of the page load would be the
        // physical tab of the first sample.
        let currentSampleTab = '#' + slugify(model.sub_samples[0].metadata.short_name);

        if (controller.currentSampleTab === '') {
            controller.currentSampleTab = currentSampleTab;
            controller.currentCategoryTab = {[currentSampleTab]: currentSampleTab + '-physical'};
        }
    }

    @action
    willTransition(transition) {
        if (transition.targetName === 'oils.index') {
            // we don't want to persist the editable state when navigating from the
            // oil properties page to the query list, and then back to properties.
            this.controllerFor('oils.show').editable = false;  // eslint-disable-line ember/no-controller-access-in-routes
        }
        else if (transition.targetName === 'oils.show' &&
                 transition.from.name === 'oils.show')
        {
            // Hitting the back button in edit, or just after completing edits
            // is not allowed.

            if (!transition.to.params.oil_id.endsWith('-TEMP') &&
                    this.controllerFor('oils.show').changesMade)  // eslint-disable-line ember/no-controller-access-in-routes
            {
                // We are making a transition to a permanent ID,
                // but changes are still in progress.  Not allowed
                transition.abort;
                this.replaceWith(transition.targetName,
                                 transition.from.attributes);
            }
            else if (transition.to.params.oil_id.endsWith('-TEMP') &&
                     !this.controllerFor('oils.show').changesMade)  // eslint-disable-line ember/no-controller-access-in-routes
            {
                // We are making a transition to a temporary ID,
                // but no changes have been made.  Not allowed.
                transition.abort;
                this.replaceWith(transition.targetName,
                                 transition.from.attributes);
            }
        }
    }
}
