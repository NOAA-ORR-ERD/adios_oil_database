import ApplicationRoute from '../application';


export default class OilsIndexRoute extends ApplicationRoute {
    model() {
        this.models = this.modelFor('oils');
        
        return this.store.peekAll('oil', {param: this.models.oil});
    }
    
    setupController(controller, model) {
        super.setupController(controller, model);
        
        controller.set('configs', this.models.configs);
        controller.set('labels', this.models.labels);
        controller.set('productTypes', this.models.productTypes);
        controller.set('capabilities', this.models.capabilities);
    }
}
