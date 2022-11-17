import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';


// We don't actually call or instantiate this class, it is just a base class
// for the other routes so we can easily support the injection of metrics.
export default class ApplicationRoute extends Route {
    @service metrics;
    @service router;

    constructor() {
        super(...arguments);

        this.router.on('routeDidChange', () => {
          const page = this.router.currentURL;
          const title = this.router.currentRouteName || 'unknown';

          this.metrics.trackPage({ page, title });
        });
    }
}
