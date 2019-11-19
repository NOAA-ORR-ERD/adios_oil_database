import DS from 'ember-data';
const { Model, attr } = DS;

export default Model.extend({
  // These attributes are used in the table columns of the search
  name: attr(),
  productType: attr(),
  location: attr(),
  reference: attr(),
  referenceDate: attr(),
  comments: attr(),
  categories: attr(),
  status: attr(),
  apis: attr(),
  viscosity: attr(),

  samples: attr()
});
