import DS from 'ember-data';
const { Model, attr } = DS;

export default Model.extend({
  // These attributes are used in the table columns of the search as well as
  // the full records
  metadata: attr(),
  status: attr(),
  subSamples: attr(),
  extraData: attr()
});
