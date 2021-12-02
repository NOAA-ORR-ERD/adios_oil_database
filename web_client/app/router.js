import EmberRouter from '@ember/routing/router';
import config from './config/environment';

class Router extends EmberRouter {
    location = config.locationType;
    rootURL = config.rootURL;
}


Router.map(function() {
    this.route('about');
    this.route('contact');
    this.route('oils', function() {
        this.route('show', { path: '/:oil_id' });
    });
    this.route('help', function() {
        this.route('show', { path: '/api/docs/' });
    });
    this.route('labels');
    this.route('product-types');
    this.route('disclaimer');
    this.route('privacy');
    this.route('capabilities');
    this.route('qa-status');
});

export default Router;
