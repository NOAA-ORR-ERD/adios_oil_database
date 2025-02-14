import { module, test } from 'qunit';
import { setupRenderingTest } from 'adios-db/tests/helpers';
import { render } from '@ember/test-helpers';
import { hbs } from 'ember-cli-htmlbars';

module('Integration | Component | dialog/review-status', function (hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function (assert) {
    // Set any properties with this.set('myProperty', 'value');
    // Handle any actions with this.set('myAction', function(val) { ... });

    await render(hbs`<Dialog::ReviewStatus />`);

    assert.dom().hasText('');

    // Template block usage:
    await render(hbs`
      <Dialog::ReviewStatus>
        template block text
      </Dialog::ReviewStatus>
    `);

    assert.dom().hasText('template block text');
  });
});
