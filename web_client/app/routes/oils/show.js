import Route from '@ember/routing/route';
import { on } from '@ember/object/evented';

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
    })

});
