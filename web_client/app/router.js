import EmberRouter from '@ember/routing/router';
import config from './config/environment';

const Router = EmberRouter.extend({
  location: config.locationType,
  rootURL: config.rootURL
});

Router.map(function() {
  this.route('about');
  this.route('contact');
  this.route('oils', function() {
    this.route('show', { path: '/:oil_id' });
  });
  this.route('labels');
  this.route('product-types');
  this.route('disclaimer');
  this.route('privacy');
});

export default Router;
