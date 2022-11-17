import ApplicationRoute from './application';


export default class CapabilitiesRoute extends ApplicationRoute {
    model() {
        return (async () => {
            let config = await this.store.findRecord('config', 'main.json');
            var adapter = await this.store.adapterFor('capability');
            
            if (adapter.host !== config.webApi) {
                adapter = await adapter.reopen({host: config.webApi});
            }
            
            return this.store.findAll('capability');
        })();
    }
}
