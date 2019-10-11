import { module, test } from 'qunit';
import { setupTest } from 'ember-qunit';

module('Unit | Route | oils/show', function(hooks) {
  setupTest(hooks);

  test('it exists', function(assert) {
    let route = this.owner.lookup('route:oils/show');
    assert.ok(route);
  });
});
