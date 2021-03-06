import Route from '@ember/routing/route';


export default class LabelsRoute extends Route {
    model() {
        return (async () => {
            let config = await this.store.findRecord('config', 'main.json');
            var adapter = await this.store.adapterFor('label');
            
            if (adapter.host !== config.webApi) {
                adapter = await adapter.reopen({host: config.webApi});
            }
            
            return this.store.findAll('label');
        })();
    }
}
