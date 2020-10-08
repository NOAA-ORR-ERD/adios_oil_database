import Route from '@ember/routing/route';
import { on } from '@ember/object/evented';
import slugify from 'ember-slugify';

export default Route.extend({
    model(params) {
        const oils = this.modelFor('oils');

        return this.store.findRecord('oil', params.oil_id, {param: oils,
            reload: true });
    },

    resetEditable: on('deactivate', function() {
        // we don't want to persist the editable state when navigating from the
        // oil properties page to the query list, and then back to properties.
        this.controller.editable = false;
    }),

    setupController(controller, model) {
        //super.setupController(controller, model);
        this._super(controller, model);

        // Our current sample tabs at the start of the page load would be the
        // physical tab of the first sample.
        let currentSampleTab = '#' + slugify(model.sub_samples[0].metadata.short_name);

        controller.currentSampleTab = currentSampleTab;
        controller.currentCategoryTab = {[currentSampleTab]: currentSampleTab + '-physical'};
    }
});
