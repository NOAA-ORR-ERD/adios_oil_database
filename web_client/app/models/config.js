import Model, { attr } from '@ember-data/model';

export default Model.extend({
    comments: attr(),
    webApi: attr(),
    template: attr()
});
