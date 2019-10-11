import DS from 'ember-data';
const { Model, attr, hasMany, belongsTo } = DS;

export default Model.extend({
  name: attr(),
  parent: belongsTo('category', { inverse: 'children' }),
  children: hasMany('category', { inverse: 'parent' })
});
