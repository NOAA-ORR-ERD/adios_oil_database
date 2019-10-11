import EmberObject from '@ember/object';
import Graph2dMixin from 'ember-oil-db/mixins/graph-2d';
import { module, test } from 'qunit';

module('Unit | Mixin | graph-2d', function() {
  // Replace this with your real tests.
  test('it works', function (assert) {
    let Graph2dObject = EmberObject.extend(Graph2dMixin);
    let subject = Graph2dObject.create();
    assert.ok(subject);
  });
});
