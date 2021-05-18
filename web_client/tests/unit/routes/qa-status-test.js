import { module, test } from 'qunit';
import { setupTest } from 'ember-qunit';

module('Unit | Route | dev-status', function(hooks) {
  setupTest(hooks);

  test('it exists', function(assert) {
    let route = this.owner.lookup('route:dev-status');
    assert.ok(route);
  });
});
