import EmberObject from '@ember/object';
import TableCommonMixin from 'ember-oil-db/mixins/table-common';
import { module, test } from 'qunit';

/* eslint-disable ember/no-new-mixins */

module('Unit | Mixin | table-common', function() {
  // Replace this with your real tests.
  test('it works', function (assert) {
    let TableCommonObject = EmberObject.extend(TableCommonMixin);
    let subject = TableCommonObject.create();
    assert.ok(subject);
  });
});

/* eslint-enable ember/no-new-mixins */
