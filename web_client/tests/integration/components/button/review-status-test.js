import { module, test } from 'qunit';
import { setupRenderingTest } from 'adios-db/tests/helpers';
import { render } from '@ember/test-helpers';
import { hbs } from 'ember-cli-htmlbars';

module('Integration | Component | button/review-status', function (hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function (assert) {
    // Set any properties with this.set('myProperty', 'value');
    // Handle any actions with this.set('myAction', function(val) { ... });

    await render(hbs`<Button::ReviewStatus />`);

    assert.dom().hasText('');

    // Template block usage:
    await render(hbs`
      <Button::ReviewStatus>
        template block text
      </Button::ReviewStatus>
    `);

    assert.dom().hasText('template block text');
  });
});
