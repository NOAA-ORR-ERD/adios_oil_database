import ApplicationRoute from './application';


export default class IndexRoute extends ApplicationRoute {
    beforeModel(/* transition */) {
        // Implicitly aborts the on-going transition.
        this.router.transitionTo('oils');
    }
}
