import Route from '@ember/routing/route';
import { scheduleOnce } from '@ember/runloop';

import $ from 'jquery';

export default Route.extend({
  model(params) {
      const oils = this.modelFor('oils');

      return this.store.findRecord('oil', params.oil_id, {param: oils,
                                                          reload: true });
  },

  actions: {
    didTransition() {
      // Any operations that need to be performed after the DOM has been
      // rendered
      scheduleOnce('afterRender', this, this.deactivateTabPanes);

      return true; // Bubble the didTransition event
    }
  },
  
  deactivateTabPanes() {
      // In order for our graphs to be properly rendered, any tab panes
      // that contain graphs need to be defined as active in the .hbs
      // template.
      // But this causes weird tab navigation behavior, where the non-active
      // tabs will not render after the initial navigation click.
      //
      // So for any tab panes that we defined as active, but don't actually
      // intend to be active initially, we undo the active state
      $( "div.tab-pane.active" ).not('.show').removeClass('active');
  }
});
