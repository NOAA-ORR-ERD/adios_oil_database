import Route from '@ember/routing/route';

export default Route.extend({
  model() {
      return (async () => {
          let config = await this.store.findRecord('config', 'main.json');
          var adapter = await this.store.adapterFor('oil');

          if (adapter.host !== config.webApi) {
            adapter = await adapter.reopen({host: config.webApi});
          }

          return this.store.peekAll('oil');
        })();
  }
});
