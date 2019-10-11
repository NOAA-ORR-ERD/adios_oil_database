import DS from 'ember-data';
const { Model, attr, hasMany } = DS;

export default Model.extend({
  // These attributes are used in the table columns of the search
  name: attr(),
  productType: attr(),
  location: attr(),
  viscosity: attr(),
  pourPoint: attr(),
  apis: attr(),
  categoriesStr: attr(),
  categories: attr(),
  status: attr(),

  // These are used in the oil details page
  reference: attr(),
  referenceDate: attr(),
  sampleDate: attr(),
  comments: attr(),
  synonyms: attr(),

  densities: attr(),
  dvis: attr(),
  kvis: attr(),
  flashPoints: attr(),
  pourPoints: attr(),
  cuts: attr(),

  ifts: attr(),
  adhesions: attr(),
  evaporationEqs: attr(),
  emulsions: attr(),
  chemicalDispersibility: attr(),
  sulfur: attr(),
  water: attr(),
  benzene: attr(),
  headspace: attr(),
  chromatography: attr(),

  ccme: attr(),
  ccmeF1: attr(),
  ccmeF2: attr(),
  ccmeTph: attr(),

  alkylatedPahs: attr(),
  biomarkers: attr(),
  waxContent: attr(),
  alkanes: attr(),
  saraTotalFractions: attr(),
  toxicities: attr(),
  conradson: attr()
});
