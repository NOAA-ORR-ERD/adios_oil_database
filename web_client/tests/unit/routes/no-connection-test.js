import { module, test } from 'qunit';
import { setupTest } from 'ember-qunit';

module('Unit | Route | no-connection', function(hooks) {
  setupTest(hooks);

  test('it exists', function(assert) {
    let route = this.owner.lookup('route:no-connection');
    assert.ok(route);
  });
});
