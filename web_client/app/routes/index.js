import ApplicationRoute from './application';


export default class IndexRoute extends ApplicationRoute {
    redirect() {
        this.transitionTo('oils');
    }
}
