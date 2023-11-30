import Route from '@ember/routing/route';
import { service } from '@ember/service';


// We don't actually call or instantiate this class, it is just a base class
// for the other routes so we can easily support the injection of metrics.
export default class ApplicationRoute extends Route {
    @service store;
    @service router;
    @service metrics;

    constructor() {
        super(...arguments);

        // ember-metrics needs this to function properly.
        // Maybe a bugfix to ember-metrics in the future will make this
        // unnecessary.
        window.dataLayer = window.dataLayer || [];

        this.router.on('routeDidChange', () => {
          const page = this.router.currentURL;
          const title = this.router.currentRouteName || 'unknown';

          this.metrics.trackPage({ page, title });
        });
    }
}
