import { module, test } from 'qunit';
import { setupTest } from 'ember-qunit';

module('Unit | Serializer | application', function(hooks) {
  setupTest(hooks);

  // Replace this with your real tests.
  test('it exists', function(assert) {
    let store = this.owner.lookup('service:store');
    let serializer = store.serializerFor('application');

    assert.ok(serializer);
  });

  //
  // This is a base serializer class, and there is no associated
  // model.  So we skip this test for now.
  //
  //test('it serializes records', function(assert) {
  //  let store = this.owner.lookup('service:store');
  //  let record = store.createRecord('application', {});
  //
  //  let serializedRecord = record.serialize();
  //
  //  assert.ok(serializedRecord);
  //});

});
